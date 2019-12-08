# -*- coding: utf-8 -*-
COPYRIGHT = "Copyright(c)2014 koo@kormail.net All rights reserved"

from gevent import monkey
monkey.patch_all()
import bottle
import handlers
import logging.config
from beaker.middleware import SessionMiddleware
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from user import UserManager
from friend import FriendManager
from post import PostManager
from version import get_version
import utilities


class ServerApp(SessionMiddleware):

    def __init__(self, name):
        self.name = name
        self.parse_config("server.ini")

        self.usermgr = UserManager(name)
        self.friendmgr = FriendManager(name, self.usermgr)
        self.postmgr = PostManager(name, self.friendmgr, self.publichost)

        self.userdb = self.usermgr.get_conn
        self.frienddb = self.friendmgr.get_conn
        self.postdb = self.postmgr.get_conn

        self.util = utilities
        super(type(self), self).__init__(bottle.app(), self.session_opts)

    def parse_config(self, config_file_name):
        logging.config.fileConfig(config_file_name)
        config = configparser.RawConfigParser()
        config.read(config_file_name)

        for option, value in config.items(self.name):
            try:
                _val = eval(value)
            except:
                _val = value
            setattr(self, option, _val)

        self.fileserver = config.get("tinyfile", "publichost")

        session_opts = {}
        for option, value in config.items("session"):
            key = "session." + option
            session_opts[key] = value
        self.session_opts = session_opts

        host, port = self.bind.split(":")
        self.host = host
        self.port = int(port)

    def plugin(self, callback):
        def wrapper(*args, **kwargs):
            body = callback(self, *args, **kwargs)
            return body
        return wrapper


if __name__ == "__main__":
    app = ServerApp("tinypost")
    logging.info("{0} {1} {2}".format(app.name,
                                      get_version(verbose=True),
                                      COPYRIGHT))

    bottle.install(app.plugin)
    bottle.run(app=app, host=app.host, port=app.port, debug=__debug__)
