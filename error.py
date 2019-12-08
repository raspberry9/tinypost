# -*- coding: utf-8 -*-
import json


# 전체 어플리케이션 에러
class ApplicationError(Exception):
    code = -1
    HTTPError = 400
    data = {}

    def _get_message(self):
        if self.args:
            return self.args[0] % (self.args[1:] if len(self.args) > 2 else [])
        else:
            return ""

    msg = property(_get_message, None)

    def to_json(self):
        res = self.data
        res.update({"code": self.code, "msg": self.msg})
        return json.dumps(res)

class NoError(ApplicationError):              code = 0; HTTPError = 200

class BadParameterError(ApplicationError):    code = -1;
class UnauthorizedError(ApplicationError):    code = -2; HTTPError = 401

class UserManagerError(ApplicationError):     code = -1000
class NoUserError(UserManagerError):          code = -1010
class UserDuplicatedError(UserManagerError):  code = -1020
class InvalidIdError(UserManagerError):       code = -1030
class InvalidPasswordError(UserManagerError): code = -1040

class FriendManagerError(ApplicationError):   code = -1100
class AlreadyFriendError(FriendManagerError): code = -1110
class BadRelationError(FriendManagerError):   code = -1120

class PostManagerError(ApplicationError):     code = -1200
class PostAccessError(ApplicationError):      code = -1210
class PostNotExistError(ApplicationError):    code = -1220
