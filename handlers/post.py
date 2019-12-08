# -*- coding: utf-8 -*-
import logging
from bottle import route
from error import NoError, ApplicationError
from .login import login_required
from http import get_response, get_request


req_proto = {'userid': str,
             'context': str,
             'images': str,
             'status': int(1)}

res_proto = {'code': int,
             'msg': str}


@route('/post', method='GET')
@login_required()
def post(app):
    """
    포스팅을 합니다.

    호출
    http://localhost:8080/post?userid=test@abc.com&context="this is posting"&images=http://www.happ.kr/images/01.jpg,http://www.happ.kr/images/02.jpg&status=1

    결과
    {"code":0, "msg":""} : 성공
    {"code":-1, "msg":"..."} : 필수 파라미터가 빠졌거나 잘못된 경우
    """
    try:
        req = get_request(req_proto)
        userid = req['userid']
        context = req['context']
        images = req['images'].split(",")
        status = req['status']

        with app.postdb() as db:
            app.postmgr.post(db, userid, images, context, status)

        return get_response(res_proto, NoError())

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
