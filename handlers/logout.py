# -*- coding: utf-8 -*-
import logging
from bottle import route
from error import NoError, ApplicationError
from login import login_required
from http import get_response, get_request


req_proto = {}

res_proto = {'code': int,
             'msg': str,}

@route('/logout', method='GET')
@login_required()
def logout(app):
    """
    로그아웃 한다.

    호출
    http://localhost:8080/logout

    결과
    {"msg": "", "code": 0} : 성공
    {"msg": "login required.", "code": -2} : 로그인 하지 않은 상태에서 로그아웃 요청
    """
    try:
        req = get_request(req_proto)
        session = req['session']
        userid = session['userid']

        session.delete()
        session.save()

        with app.userdb() as db:
            app.usermgr.logout(db, userid)

        return get_response(res_proto, NoError())

    except ApplicationError as e:
        logging.debug(e)
        return get_response(res_proto, e)

    except Exception as e:
        logging.exception(e)
