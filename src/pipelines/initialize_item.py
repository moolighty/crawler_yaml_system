#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""将item没有的字段进行初始化,补充默认值"""

import logging

from src.items import BaseItem

log = logging.getLogger(__name__)


class InitializeItemPipeline(object):
    """item初始化并设置域名"""

    def process_item(self, item, spider):
        default_item = BaseItem.init_item()
        default_item.update(item)
        default_item = BaseItem.set_site_domain(default_item)
        default_item = BaseItem.set_category(default_item)
        return default_item
