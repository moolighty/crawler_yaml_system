#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""Helper functions which don't fit anywheres else"""

import logging

from importlib import import_module
from scrapy.utils.misc import load_object as load

log = logging.getLogger(__name__)


def load_module_attributes(module, key_prefix=''):
    """得到模块的全部属性和值,以dict形式返回, """
    if not module:
        log.warn("module:{} 传入不合法,找不到该module".format(module))
        return {}

    try:
        if isinstance(module, str):
            module = import_module(module)
    except Exception as e:
        log.error("加载module:{} 发生异常:{}".format(module, e))
        return {}

    attributes = {}
    for key in dir(module):
        temp_key = key.lower()
        if key_prefix:
            if key.startswith(key_prefix):
                attributes[temp_key] = getattr(module, key)
        else:
            # 去掉魔术属性
            if not key.startswith('__'):
                attributes[temp_key] = getattr(module, key)
    return attributes


def load_object(object_path, default_object=None):
    try:
        return load(object_path)
    except Exception as e:
        log.error("加载'{}' 发生异常,异常原因如下:{}".format(object_path, e))
        return default_object
