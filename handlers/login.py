# -*- coding: utf-8 -*-
import time
import logging
from bottle import route, request
from error import NoError, ApplicationError, UnauthorizedError
from http import get_response, get_request


req_proto = {'userid': str,
             'password': str,}

res_proto = {'code': int,
             'msg': str,}

def login_required():
    """
    로그인 되어 있지 않으면
    {"msg": "login required.", "code": -2}
    오류를 반환한다.
    """
    def wrap(fn):
        def login_checker(app, *args, **kwargs):
            if 'userid' not in request.environ.get('beaker.session').keys():
                return get_response(res_proto, UnauthorizedError("login required."))
            return fn(app, *args, **kwargs)
        return login_checker
    return wrap

@route('/login', method='GET')
def login(app):
    """
    로그인을 처리 합니다.

    호출
    http://localhost:8080/login?userid=test@abc.com&password=1234

    결과
    {"code":0, "msg":""} : 성공
    {"code":-1, "msg":"..."} : 필수 파라미터가 빠졌거나 잘못된 경우
    """
    try:
        req = get_request(req_proto)
        userid = str(req['userid'])
        password = req['password']

        with app.userdb() as db:
            user = app.usermgr.login(db, userid, password)

        session = req['session']
        session['num'] = user.num
        session['userid'] = user.id
        session['nickname'] = user.nickname
        session['lastlogin'] = time.time()
        session['ip'] = request.remote_addr
        session.save()

	return get_response(res_proto, NoError())

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
