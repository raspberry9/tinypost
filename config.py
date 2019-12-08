# -*- coding: utf-8 -*-
import logging
import configparser

class Config(object):

    def __init__(self, filename):
        logging.config.fileConfig(filename)
        config = configparser.RawConfigParser()
        config.read(filename)

        for option, value in config.items(self.name):
            try:
                 _val = eval(value)
            except:
                 _val = value
            setattr(self, option, _val)
             
        session_opts = {}
        for option, value in config.items("session"):
            key = "session." + option
            session_opts[key] = value
        self.session_opts = session_opts
         
        host, port = self.bind.split(":")
        self.host = host
        self.port = int(port)

