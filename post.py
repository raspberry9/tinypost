# -*- coding: utf-8 -*-
from dataobj import dataobj, dataobjmanager
from error import PostAccessError, PostNotExistError


class PostManager(dataobjmanager):

    """
    """
    # Default Enumerations
    URL = "0.0.0.0:8080"

    ITEMS_PER_PAGE = 10  # 한 페이지에 보여질 포스팅 수

    POST_NOTICE = 0     # 포스팅 없음
    POST_PRIVATE = 1    # 개인적인 글 : 작성자만 열람 가능
    POST_FRIENDS = 2    # 친구 공개 글 : 작성자 및 작성자와 서로 친구인 사용자만 열람 가능
    POST_PUBLIC = 3     # 전체 공개 글 : 모든 사용자가 열람 가능

    # Database Schema
    TABLE_NAME = "posts"
    TABLE_DEFINATION = [
        "num INTEGER PRIMARY KEY AUTOINCREMENT",
        "wnum INTEGER",
        "wtime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL",
        "status INTEGER DEFAULT 0 NOT NULL",
        "images STRING",
        "context STRING", ]
        #"!CREATE INDEX writer_idx ON posts (wnum);",]
    TABLE_FIELDS = [x.split()[0] for x in TABLE_DEFINATION if not x.lower().startswith("primary key") and not x.startswith("!")]

    def __init__(self, dbname, friendmgr, publichost):
        super(self.__class__, self).__init__(dbname)

        self.friendmgr = friendmgr
        self.usermgr = friendmgr.usermgr
        self.url = "http://{0}".format(publichost)

        # 데이터베이스에 users테이블이 없으면 생성한다.
        with self.get_conn() as db:
            self.set_table(db, self.TABLE_NAME, self.TABLE_DEFINATION)

    def get_readable_post_types(self, db, userid, readerid):
        """
        userid의 포스팅 중 userid와 readerid간의 관계에 따라 접근 가능한 포스팅 타입만 뽑아 리스트로 반환한다.
        FriendManager.POST_PRIVATE : 개인적인 글. 나만 볼 수 있다.
        FriendManager.POST_FRIENDS : 친구 허용 글. 나와 친구만 볼 수 있다.
        FriendManager.POST_PUBLIC : 공개적인 글. 모두가 볼 수 있다.
        """
        if readerid is None:
            return [self.POST_PUBLIC, ]
        elif userid == readerid:
            return [self.POST_PRIVATE, self.POST_FRIENDS, self.POST_PUBLIC]
        elif self.friendmgr.get_relation(db, userid, readerid) is self.friendmgr.RELATION_FRIEND:
            return [self.POST_FRIENDS, self.POST_PUBLIC]
        else:
            return [self.POST_PUBLIC, ]

    def get_posts(self, db, userid, readerid, page=1):
        """
        """
        readable_post_types = self.get_readable_post_types(db, userid, readerid)

        user = self.usermgr.get_user(db, userid)
        pages = self.get_page_count(db, userid, readable_post_types)
        cur = (page - 1) * self.ITEMS_PER_PAGE

        if page == 0:
            # 전체 페이지
            posts = self.query_obj(db, Post, "SELECT {0} FROM posts WHERE wnum=? and status in ({1}) ORDER BY num DESC".format(", ".join(self.TABLE_FIELDS), ", ".join(map(str, readable_post_types))), (user.num,))
        else:
            # 일부 페이지만
            posts = self.query_obj(db, Post, "SELECT {0} FROM posts WHERE wnum=? and status in ({1}) ORDER BY num DESC LIMIT ? OFFSET ?".format(", ".join(self.TABLE_FIELDS), ", ".join(map(str, readable_post_types))), (user.num, self.ITEMS_PER_PAGE, cur))

        for post in posts:
            setattr(post, "wid", user.id)
            setattr(post, "wnick", user.nickname)
            setattr(post, "curpage", page)
            setattr(post, "pages", pages)
        return posts

    def get_friends_posts(self, db, userid, page=1):
        readable_post_types = [self.POST_PUBLIC, self.POST_FRIENDS]

        mutual_friendid_list = self.friendmgr.get_mutual_friendid_list(db, userid)
        friends = self.usermgr.get_users(db, mutual_friendid_list)
        fmap = {friend.num: friend for friend in friends}
        pages = self.get_page_count(db, mutual_friendid_list, readable_post_types)
        cur = (page - 1) * self.ITEMS_PER_PAGE
        posts = self.query_obj(db, Post, "SELECT {0} FROM posts WHERE wnum in ({1}) and status in ({2}) ORDER BY num DESC LIMIT ? OFFSET ?".format(", ".join(self.TABLE_FIELDS), ", ".join(["'%s'" % (x,) for x in fmap.keys()]), ", ".join(map(str, readable_post_types))), (self.ITEMS_PER_PAGE, cur))
        for post in posts:
            setattr(post, "wid", fmap[post.wnum].id)
            setattr(post, "wnick", fmap[post.wnum].nickname)
            setattr(post, "curpage", page)
            setattr(post, "pages", pages)
        return posts

    def post(self, db, userid, images, context, status=POST_PRIVATE):
        wnum = self.usermgr.get_num_from_id(db, userid)
        if isinstance(images, type(list)):
            _images = ",".join(map(str, images))
        else:
            _images = str(images)
        self.query(db, "INSERT INTO posts (wnum, status, images, context) VALUES (?, ?, ?, ?)", (wnum, status, _images, context))

    def get_post(self, db, num, readerid=None):
        post = self.query_obj_one(db, Post, "SELECT {0} FROM posts WHERE num=?".format(", ".join(self.TABLE_FIELDS)), (num,))
        if not post:
            raise PostNotExistError("post is not exist. post_num=%s, readerid=%s" % (num, readerid))
        writerid = self.usermgr.get_id_from_num(db, post.wnum)
        if not readerid:
            readerble_post_types = [self.POST_PUBLIC, ]
        else:
            readerble_post_types = self.get_readable_post_types(db, writerid, readerid)

        if post.status in readerble_post_types:
            writer = self.usermgr.get_user(db, writerid)
            setattr(post, "wid", writer.id)
            setattr(post, "wnick", writer.nickname)
            setattr(post, "curpage", 1)
            setattr(post, "pages", 1)
            return post

        raise PostAccessError("post access privilege error. writerid=%s, reader=%s, post_num=%s, post_status=%s" % (writerid, readerid, post.num, post.status))

    def update_post(self, db, num, status, images, context):
        if isinstance(images, type(list)):
            _images = ",".join(map(str, images))
        else:
            _images = str(images)
        self.query(db, "UPDATE posts set status=?, images=?, context=? WHERE num=?", (status, _images, context))

    def remove_post(self, db, num):
        self.query(db, "DELETE posts WHERE num=?", (num,))

    def get_page_count(self, db, userid_or_userids, readable_post_types):
        if isinstance(userid_or_userids, str):
            userid_list = [userid_or_userids, ]
        elif isinstance(userid_or_userids, list):
            userid_list = userid_or_userids

        wnums = [self.usermgr.get_num_from_id(db, userid) for userid in userid_list]
        rs = self.query(db, "SELECT count(*) FROM posts WHERE wnum in ({0}) and status in ({1})".format(", ".join(map(str, wnums)), ", ".join(map(str, readable_post_types))))
        post_count = int(rs[0][0]) if rs else 0
        return int(post_count / self.ITEMS_PER_PAGE) + 1

    def convert_posts_to_rss(self, posts):
        """
        Post 객체 리스트를 rss 형식으로 변환한다.
        """
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<rss version="2.0">\n'
                '\t<channel>\n'
                '\t\t<title>tinypost</title>\n'
                '\t\t<generator>tinypost 0.1</generator>\n'
                '\t\t<link>{0}</link>\n{1}\n'
                '\t</channel>\n'
                '</rss>'.format(self.url, "\n".join(["\n".join(["\t\t\t%s" % i for i in item.to_xml(self.url).split("\n")]) for item in posts])).replace("\t", "    "))


class Post(dataobj):
    TABLE_FIELDS = PostManager.TABLE_FIELDS

    def to_xml(self, url):
        """
        rss 피드 형식의 아이템 스트링을 반환 한다.
        """
        title = self.context.split('\n')[0]
        if len(title) > 80:
            title = title[0:77] + u"..."
        link = url + "/feed?num={0}".format(self.num)
        author = u"%s(%s)" % (self.wnick, self.wid)
        return u'<item>\n<title>{0}</title>\n\t<link>{1}</link>\n\t<author>{2}</author>\n\t<description>{3}</description>\n\t<pubDate>{4}</pubDate>\n\t<guid>{5}</guid>\n</item>'.format(title, link, author, self.context, self.wtime, link)
