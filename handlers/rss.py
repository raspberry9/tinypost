# -*- coding: utf-8 -*-
import logging
from bottle import route, response
from error import ApplicationError
from login import login_required
from http import get_response, get_request


req_proto = {'userid': str,
             'page': int(1)}

res_proto = {'code': int,
             'msg': str,
             'rss': str,
             'curpage': int(1),
             'allpages': int(1),}

@route('/rss', method='GET')
@login_required()
def rss(app):
    """
    포스팅한 내용을 rss 형식으로 리턴 합니다.

    호출
    http://localhost:8080/rss?userid=test@abc.com&page=1

    결과
    {"code":0, "msg":"", "rss":"<?xml...>", "curpage":1, "allpages":10} : 성공
    {"code":-1, "msg":"..."} : 필수 파라미터가 빠졌거나 잘못된 경우
    """
    try:
        req = get_request(req_proto)
        session = req['session']
        readerid = str(session['userid'])
        userid = str(req['userid'])
        page = int(req['page'])

        with app.postdb() as db:
            posts = app.postmgr.get_posts(db, userid, readerid, page)

        rss = app.postmgr.convert_posts_to_rss(posts)

        response.content_type = 'application/xml'

        return rss

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
