# -*- coding: utf-8 -*-
import re
import json
from dataobj import dataobj, dataobjmanager
from error import (NoUserError,
                   UserDuplicatedError,
                   InvalidIdError,
                   InvalidPasswordError,)


class UserManager(dataobjmanager):
    """
    """
    # Default Enumerations
    MIN_ID_LENGTH = 7                       # 최소 아이디 길이
    MAX_ID_LENGTH = 320                     # 최대 아이디 길이
    MIN_PASSWORD_LENGTH = 4                 # 최소 비밀번호 길이
    MAX_PASSWORD_LENGTH = 256               # 최대 비밀번호 길이
    EMAIL_PATTERN = r'[\w.-]+@[\w.-]+.\w+'  # 이메일 regex 패턴

    # Database Schema
    TABLE_NAME = "users"
    TABLE_DEFINATION = [
        "num INTEGER PRIMARY KEY AUTOINCREMENT",
        "id STRING UNIQUE NOT NULL",
        "password STRING NOT NULL",
        "nickname STRING NOT NULL",
        "jointime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL",
        "logintime TIMESTAMP DEFAULT NULL",
        "profile STRING DEFAULT ''",
        "data STRING DEFAULT ''",
        "type INTEGER DEFAULT 0 NOT NULL",
        "status INTEGER DEFAULT 0 NOT NULL",]
    TABLE_FIELDS = [x.split()[0] for x in TABLE_DEFINATION if not x.lower().startswith("primary key") and not x.startswith("!")]

    def __init__(self, dbname):
        super(self.__class__, self).__init__(dbname)

        # 데이터베이스에 users테이블이 없으면 생성한다.
        with self.get_conn() as db:
            self.set_table(db, self.TABLE_NAME, self.TABLE_DEFINATION, ["password",])

    def _check_id(self, userid):
        """
        아이디 형식을 검사한다.
        """
        if not isinstance(userid, str) and not isinstance(userid, unicode):
            raise InvalidIdError("type of userid is not vaild. userid=%s, type=%s" % (userid, type(userid)))
        if not(self.MIN_ID_LENGTH <= len(userid) <= self.MAX_ID_LENGTH):
            raise InvalidIdError("length of userid is not correct. userid=%s, length=%s, min=%s, max=%s" % (userid, len(userid), self.MIN_ID_LENGTH, self.MAX_ID_LENGTH))
        if not re.search(self.EMAIL_PATTERN, userid):
            raise InvalidIdError("userid is not email type. userid=%s" % (userid,))

    def _check_password(self, password):
        """
        비밀번호 형식을 검사한다.
        """
        if not(self.MIN_PASSWORD_LENGTH <= len(password) <= self.MAX_PASSWORD_LENGTH):
            raise InvalidPasswordError("length of password is not correct. length=%s, min=%s, max=%s" % (len(password), self.MIN_PASSWORD_LENGTH, self.MAX_ID_LENGTH))

    def get_num_from_id(self, db, userid):
        """
        userid를 사용자 번호로 변환 한다.
        """
        self._check_id(userid)
        return self.query(db, "SELECT num FROM users WHERE id=?", (userid,))[0][0]

    def get_id_from_num(self, db, num):
        """
        사용자 번호를 userid로 변환 한다.
        """
        return self.query(db, "SELECT id FROM users WHERE num=?", (num,))[0][0]

    def login(self, db, userid, password):
        self._check_id(userid)
        self._check_password(password)
        user = self.query_obj_one(db, User, "SELECT {0} FROM users WHERE id=? and password=?".format(", ".join(self.TABLE_FIELDS)), (userid, password))
        if not user:
            raise NoUserError("user is not exist or password is not correct. userid=%s" % (userid,))

        return user

    def logout(self, db, userid):
        self._check_id(userid)
        pass

    def join(self, db, userid, password, nickname):
        self._check_id(userid)
        self._check_password(password)
        try:
            self.query(db, "INSERT INTO users (id, password, nickname) VALUES (?, ?, ?)", (userid, password, nickname))
        except:
            raise UserDuplicatedError("join user is duplicated. userid=%s" % (userid,))

    def withdraw(self, db, userid):
        self._check_id(userid)
        self.query(db, "DELETE FROM users WHERE id=?", (userid,))

    def get_user(self, db, userid):
        self._check_id(userid)
        user = self.query_obj_one(db, User, "SELECT {0} FROM users WHERE id=?".format(", ".join(self.TABLE_FIELDS)), (userid,))
        if not user:
            raise NoUserError("user is not exist. userid=%s" % (userid,))
        return user

    def get_users(self, db, userid_list):
        _userid_list = []
        for userid in userid_list:
            try:
                self._check_id(userid)
                _userid_list.append("'"+userid+"'")
            except:
                pass

        return self.query_obj(db, User, "SELECT {0} FROM users WHERE id in ({1})".format(", ".join(self.TABLE_FIELDS), ", ".join(_userid_list)))

    # --------------------------------------------------------------------------
    # 사용자 프로필 관련 함수들
    # --------------------------------------------------------------------------
    def get_profile(self, db, userid):
        user = self.get_user(db, userid)
        return json.loads(user.profile) if user.profile else {}

    def set_profile(self, db, userid, profile):
        self._check_id(userid)
        self.query(db, "UPDATE users SET profile=? WHERE id=?", (json.dumps(profile), userid))

    def update_profile(self, db, userid, attribute, value):
        self._check_id(userid)
        profile = self.get_profile(db, userid)
        profile.update({attribute: value})
        self.set_profile(db, userid, profile)

    def update_today_message(self, db, userid, msg):
        self.update_profile(db, userid, "tmsg", msg)

    def update_image_url(self, db, userid, url):
        self.update_profile(db, userid, "img", url)


class User(dataobj):
    TABLE_FIELDS = UserManager.TABLE_FIELDS

    def get_profile(self):
        return json.loads(self.profile)

    def set_profile(self, profile):
        if not isinstance(profile, str):
            profile = json.dumps(profile)

        setattr(self, "profile", profile)
