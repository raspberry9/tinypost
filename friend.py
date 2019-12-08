# -*- coding: utf-8 -*-
from dataobj import dataobjmanager
from error import AlreadyFriendError, BadRelationError


class FriendManager(dataobjmanager):
    """
    """
    # Default Enumerations
    RELATION_NONE = 0     # 관계 없음(삭제)
    RELATION_INVITED = 1  # 친구 요청 받음
    RELATION_FRIEND = 2   # 친구
    RELATION_DECLINE = 3  # 친구 거절(다시 친구 요청 불가)

    # Database Schema
    TABLE_NAME = "friends"
    TABLE_DEFINATION = [
        "num INTEGER",
        "friendnum INTEGER",
        "etime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL",
        "status INTEGER NOT NULL",
        "primary key (num, friendnum)",]
    TABLE_FIELDS = [x.split()[0] for x in TABLE_DEFINATION if not x.lower().startswith("primary key") and not x.startswith("!")]

    def __init__(self, dbname, usermgr):
        super(self.__class__, self).__init__(dbname)

        self.usermgr = usermgr

        # 데이터베이스에 users테이블이 없으면 생성한다.
        with self.get_conn() as db:
            self.set_table(db, self.TABLE_NAME, self.TABLE_DEFINATION)

    def get_friendid_list(self, db, userid, relation=RELATION_FRIEND):
        """
        친구 목록을 userid 리스트로 반환한다.
        """
        return self.get_relation_userid_list(db, userid, relation)

    def get_mutual_friendid_list(self, db, userid):
        """
        서로 친구인 userid 리스트를 반환한다.
        """
        friendid_list = self.get_friendid_list(db, userid)
        # print "fidlst:", friendid_list
        result = [friendid for friendid in friendid_list if self.get_relation(db, friendid, userid) is self.RELATION_FRIEND]
        # print 'friendid_list=%s, result=%s' % (friendid_list, result)
        return result

    def get_relation_userid_list(self, db, userid, relation):
        """
        relation으로 지정한 관계의 유저 목록을 userid 리스트로 반환한다.
        """
        num = self.usermgr.get_num_from_id(db, userid)
        fnums = [rs[0] for rs in self.query(db, "SELECT friendnum FROM friends WHERE num=? and status=?", (num, relation))]
        return [self.usermgr.get_id_from_num(db, fnum) for fnum in fnums]

    def get_friends(self, db, userid):
        """
        친구 목록을 User객체 리스트로 반환한다.
        """
        friendid_list = self.get_friendid_list(db, userid, self.RELATION_FRIEND)
        return self.usermgr.get_users(db, friendid_list)

    def get_relation(self, db, userid, friendid):
        """
        userid와 friendid간의 관계를 반환한다.
        FriendManager.RELATION_NONE : 관계 없음. 관계 정보가 삭제됨을 의미한다.
        FriendManager.RELATION_INVITED : userid 유저가 friendid로 부터 친구 요청을 받은 상태
        FriendManager.RELATION_FRIEND : userid와 friendid가 친구인 상태. 단, friendid는 아직 친구 수락을 한 상태가 아닐 수 있다.
        FriendManager.RELATION_DECLINE : userid가 friendid의 친구 요청을 거절한 상태
        """
        num = self.usermgr.get_num_from_id(db, userid)
        fnum = self.usermgr.get_num_from_id(db, friendid)
        rs = self.query(db, "SELECT status FROM friends WHERE num=? and friendnum=?", (num, fnum))
        return int(rs[0][0]) if rs else self.RELATION_NONE

    def invite(self, db, userid, friendid):
        """
        userid가 friendid에게 친구를 신청한다.
        userid입장에서는 바로 친구로 추가(RELATION_FRIEND)되고 상대방은 친구 요청 상태(RELATION_INVITED)가 된다.
        """
        self.usermgr._check_id(userid)
        self.usermgr._check_id(friendid)

        if self.get_relation(db, userid, friendid) is self.RELATION_FRIEND:
            # 이미 내 친구인 경우 : 에러
            raise AlreadyFriendError("userid=%s, invite_user_id=%s", userid, friendid)
        elif self.get_relation(db, friendid, userid) is self.RELATION_FRIEND:
            # 이미 상대방이 나에게 친구 신청을 해 놓은 경우 : 바로 친구를 맺어준다.
            self._update_relation(db, userid, friendid, self.RELATION_FRIEND)
        else:
            # 친구를 초대 한다.
            self._update_relation(db, userid, friendid, self.RELATION_FRIEND)
            self._update_relation(db, friendid, userid, self.RELATION_INVITED)

        return True

    def accept(self, db, userid, friendid):
        """
        friendid가 userid에게 요청한 친구 요청을 수락한다.
        단, 친구 요청 상태일 경우에만 accept가 가능하다.
        그렇지 않으면 FriendManagerError.BadRelationError가 발생한다.
        """
        self.usermgr._check_id(userid)
        self.usermgr._check_id(friendid)

        status = self.get_relation(db, userid, friendid)
        if status is self.RELATION_INVITED:
            self._update_relation(db, userid, friendid, self.RELATION_FRIEND)
            return True

        raise BadRelationError("userid=%s, friendid=%s, status=%s", userid, friendid, status)

    def decline(self, db, userid, friendid):
        """
        friendid가 userid에게 요청한 친구 요청을 거절한다.
        단, 친구 요청 상태일 경우에만 decline이 가능하다.
        그렇지 않으면 FriendManagerError.BadRelationError가 발생한다.
        """
        self.usermgr._check_id(userid)
        self.usermgr._check_id(friendid)

        status = self.get_relation(db, userid, friendid)
        if status is self.RELATION_INVITED:
            self._update_relation(db, userid, friendid, self.RELATION_DECLINE)
            return True

        raise BadRelationError("userid=%s, friendid=%s, status=%s", userid, friendid, status)

    def unfriend(self, db, userid, friendid):
        """
        friendid가 userid에게 요청한 친구 요청을 취소한다.
        단, 친구 상태일 경우에만 unfriend가 가능하다.
        그렇지 않으면 FriendManagerError.BadRelationError가 발생한다.
        상대방이 친구 수락을 하지 않은 상태에서 unfriend를 하면 친구 요청이 삭제 된다.
        """
        self.usermgr._check_id(userid)
        self.usermgr._check_id(friendid)

        status = self.get_relation(db, userid, friendid)
        if status is self.RELATION_FRIEND:
            self._update_relation(db, userid, friendid, self.RELATION_NONE)
            if self.get_relation(db, friendid, userid) is self.RELATION_INVITED:
                self._update_relation(db, friendid, userid, self.RELATION_NONE)
            return True

        raise BadRelationError("userid=%s, friendid=%s, status=%s", userid, friendid, status)

    def _update_relation(self, db, userid, friendid, relation):
        """
        userid와 friendid의 관계를 갱신한다.
        FriendManager.RELATION_NONE : 관계 없음. 관계 정보가 삭제됨을 의미한다.
        FriendManager.RELATION_INVITED : userid 유저가 friendid로 부터 친구 요청을 받은 상태
        FriendManager.RELATION_FRIEND : userid와 friendid가 친구인 상태. 단, friendid는 아직 친구 수락을 한 상태가 아닐 수 있다.
        FriendManager.RELATION_DECLINE : userid가 friendid의 친구 요청을 거절한 상태
        """
        num = self.usermgr.get_num_from_id(db, userid)
        fnum = self.usermgr.get_num_from_id(db, friendid)

        if relation is self.RELATION_NONE:
            self.query(db, "DELETE FROM friends WHERE num=? and friendnum=?", (num, fnum))
        else:
            self.query(db, "INSERT OR REPLACE INTO friends (num, friendnum, status) VALUES (?, ?, ?)", (num, fnum, relation))

        return True
