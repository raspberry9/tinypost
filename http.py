# -*- coding: utf-8 -*-
import json
import bottle
from bottle import request
from error import BadParameterError, ApplicationError


def get_request(proto):
    req = {}
    for k, default in proto.iteritems():
        try:
            if type(default) == type(type):
                req[k] = default(bottle.request.GET[k])
            else:
                req[k] = type(default)(bottle.request.GET[k])

        except KeyError:
            if type(default) is type(type):
                raise BadParameterError('essential request parameter is not in parameters. '
                                        'param=%s, optional=%s, essential=%s' %
                                        (k,
                                        [param for param, ptype in proto.iteritems() if type(ptype) is not type(type)],
                                        [param for param, ptype in proto.iteritems() if type(ptype) is type(type)]))
            else:
                req[k] = default
        except ValueError:
            raise BadParameterError('parameter value error. param=%s(%s), type=%s' % (k, type(request.GET[k]), default))

    req['session'] = bottle.request.environ.get('beaker.session')

    return req

def get_response(proto, err):
    bottle.response.content_type = 'application/json'

    res = {}
    if not isinstance(err, ApplicationError):
        res['code'] = -1
        res['msg'] = "unknown error."

        return json.dumps(res)
    else:
        res['code'] = err.code
        res['msg'] = err.msg

    for k, default in proto.iteritems():
        try:
            if type(default) == type(type):
                res[k] = default(getattr(err, k))
            else:
                res[k] = type(default)(getattr(err, k))
        except AttributeError:
            if hasattr(err, 'data'):
                if type(default) == type(type):
                    try:
                        res[k] = default(getattr(err, 'data')[k])
                    except KeyError:
                        if res['code'] == 0:
                            # err에 protocol에 있는 변수들이 없을 수도 있다.
                            # 따라서 성공일 경우에만 프로토콜 검사를 하면 된다.
                            res = BadParameterError('non optional response parameter is not in parameters. '
                                                    'param=%s, optional=%s, non optional=%s' %
                                                    (k,
                                                    [param for param, ptype in proto.iteritems() if ptype is type(type)],
                                                    [param for param, ptype in proto.iteritems() if ptype is not type(type)]))
                else:
                    try:
                        res[k] = type(default)(getattr(err, 'data')[k])
                    except KeyError:
                        res[k] = default

            elif type(default) == type(type):
                res = BadParameterError('non optional response parameter is not in parameters. '
                                        'param=%s, optional=%s, non optional=%s' %
                                        (k,
                                        [param for param, ptype in proto.iteritems() if ptype is type(type)],
                                        [param for param, ptype in proto.iteritems() if ptype is not type(type)]))
            else:
                res[k] = default

    return json.dumps(res)
