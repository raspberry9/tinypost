# -*- coding: utf-8 -*-
import logging
from bottle import route
from error import NoError, ApplicationError, PostNotExistError
from http import get_response, get_request


req_proto = {'num': int,} # 보고싶은 포스팅 번호

res_proto = {'code': int,
             'msg': str,
             'num': int,
             'wtime': str,
             'status': int,
             'images': str,
             'context': str,
             'wnick': unicode,}

@route('/show', method='GET')
def show(app):
    """
    포스팅한 내용을 rss 형식으로 리턴 합니다.

    호출
    http://localhost:8080/show?num=1

    결과
    {"code":0, "msg":"", "num": 1, "wid":"test@abc.com", "wnick":"test", "wtime":"2014-..",
     "status":1, "images":"http://...jpg,http://...jpg", "context": "bla, bla..."} : 성공
    {"code":-1, "msg":"..."} : 필수 파라미터가 빠졌거나 잘못된 경우
    """
    try:
        req = get_request(req_proto)
        try:
            session = req['session']
            readerid = str(session['userid'])
        except KeyError:
            # 세션이 없는 경우는 로그인 하지 않았으므로 public 글만 볼 수 있다.
            readerid = None

        num = int(req['num'])

        with app.postdb() as db:
            post = app.postmgr.get_post(db, num, readerid)

        res = NoError()
        if post:
            res.num = post.num
            res.wtime = post.wtime
            res.status = post.status
            res.images = post.images
            res.context = post.context
            res.wnick = post.wnick
        else:
            raise PostNotExistError("post not exist. readerid=%s, post_num=%s" % (readerid, num))

        return get_response(res_proto, res)

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
