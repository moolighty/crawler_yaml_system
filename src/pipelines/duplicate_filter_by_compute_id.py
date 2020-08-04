#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""去重pipeline定义"""

import json
import logging

from scrapy.utils.misc import load_object
from scrapy.exceptions import DropItem

log = logging.getLogger(__name__)


class DuplicatesFilterByComputeIdPipeline(object):
    """对item进行过滤去重, 去重之前可能需要计算_id"""

    def __init__(self):
        self.ids_seen = set()
        self.flag = True    # 去重标记

    def process_item(self, item, spider):
        rules = spider.config.get("item_reduplicate_rules")
        self.flag = rules.get('reduplicate_flag')

        # 检查是否计算_id
        if "_id" not in item or not item["_id"].strip():
            _id = self._compute_item_id(item, rules)
            if not _id:
                raise DropItem("计算 item id 失败!")
            item["_id"] = _id

        # 检查去否去重
        if self.flag:
            if item['_id'] in self.ids_seen:
                raise DropItem("item id：{} 重复, 已经存在!".format(item['_id']))
            else:
                self.ids_seen.add(item["_id"])

        return item

    def _compute_item_id(self, item, rules):
        try:
            fields = rules.get("fields")
            method = load_object(rules.get("id_compute_method"))
            s = ''
            for field in fields:
                temp = item.get(field)
                if isinstance(temp, str):
                    s += temp
                else:
                    s += json.dumps(temp)
            return method(s)
        except Exception as e:
            log.error("计算item id发生异常, 异常为{}".format(e))
        return None
