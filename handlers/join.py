# -*- coding: utf-8 -*-
import logging
from bottle import route
from error import NoError, ApplicationError
from http import get_response, get_request


req_proto = {'userid': str,
             'nickname': str,
             'password': str,
             'desc': str("")}

res_proto = {'code': int,
             'msg': str}

@route('/join', method='GET')
def join(app):
    """
    가입을 처리 합니다.

    호출
    http://localhost:8080/join?userid=test@abc.com&nickname=MyNickname&password=1234

    결과
    {"code":0, "msg":""} : 성공
    {"code":-1, "msg":"..."} : 필수 파라미터가 빠졌거나 잘못된 경우
    {"code":-1020, "msg":"..."} : 이미 해당 아이디가 존재하는 경우
    {"code":-1030, "msg":"..."} : 잘못된 아이디(길이, 형식)
    {"code":-1040, "msg":"..."} : 잘못된 비밀번호(길이, 형식)
    """
    try:
        req = get_request(req_proto)
        userid = str(req['userid'])
        nickname = unicode(req['nickname'])
        password = req['password']

        with app.userdb() as db:
            app.usermgr.join(db, userid, password, nickname)

	return get_response(res_proto, NoError())

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
