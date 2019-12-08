# -*- coding: utf-8 -*-
import time
import datetime


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400


class TimeUtil(object):
    @staticmethod
    def is_yesterday(timestamp, basetime=None):
        now = basetime if basetime else time.time()
        timediff = now - timestamp

        if TimeUtil.get_midnight(now) == TimeUtil.get_midnight(timestamp) + SECONDS_PER_DAY:
            return True
        else:            
           return False

    @staticmethod
    def is_today(timestamp, basetime=None):
        now = basetime if basetime else time.time()
        timediff = now - timestamp

        if TimeUtil.get_midnight(now) == TimeUtil.get_midnight(timestamp):
            return True
        else:
            return False

    @staticmethod
    def is_this_month(timestamp, basetime=None):
        now = basetime if basetime else time.time()
        now_dt = datetime.datetime.fromtimestamp(now)
        dt = datetime.datetime.fromtimestamp(timestamp)

        if TimeUtil.is_this_year() and now_dt.month == dt.month:
            return True
        else:
            return False

    @staticmethod
    def is_this_year(timestamp, basetime=None):
        now = basetime if basetime else time.time()

        now_dt = datetime.datetime.fromtimestamp(now)
        dt = datetime.datetime.fromtimestamp(timestamp)

        if now_dt.year == dt.year:
            return True
        else:
           return False

    @staticmethod
    def get_midnight(timestamp):
        return int(timestamp / SECONDS_PER_DAY)

    @staticmethod
    def get_human_readable_time(timestamp, basetime=None):
        now = basetime if basetime else time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
    
        if TimeUtil.is_today(timestamp, now):
            date_text = ""
        elif TimeUtil.is_yesterday(timestamp, now):
            date_text = "어제"
        else:
            date_text = "{0}년 {1}월 {2}일".format(dt.year, dt.month, dt.day)

        timediff = now - timestamp
        if timediff < SECONDS_PER_MINUTE:
            time_text = "방금 전"
        elif timediff < SECONDS_PER_HOUR:
            time_text = "{0}분 전".format(int(timediff / SECONDS_PER_MINUTE))
        elif timediff < SECONDS_PER_DAY:
            time_text = "{0}시간 전".format(int(timediff / SECONDS_PER_HOUR))
        else:
            time_text = "{0}시 {1}분 {2}초".format(dt.hour, dt.minute, dt.second)
    
        return " ".join([date_text, time_text])
