# -*- coding: utf-8 -*-

"""时间转化实用函数"""

import logging
import time
from datetime import datetime

log = logging.getLogger(__name__)


def get_now_str():
    """得到现在的时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def chinese_time_str2date_str(s):
    '''
    :param s: 2018年04月12日
    :return: 2018-04-12 00:00:00
    '''
    try:
        return datetime.strptime(s, "%Y年%m月%d日").strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        log.error("转化时间:{} 发生异常{}".format(s, e))
        return None


def get_uc_date_time_str():
    """Return the current UTC date and time"""
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_now_timestamp_second_str():
    """返回当前时间戳字符串形式, 单位为s"""
    return str(int(time.time()))


def get_now_timestamp_millisecond_str():
    """返回当前时间戳字符串形式, 单位为ms"""
    t = time.time()
    t *= 1000
    return str(int(t))