#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""检查item_fields有效性的pipeline"""

import logging
import json

from scrapy.utils.misc import load_object
from scrapy.exceptions import DropItem

log = logging.getLogger(__name__)


class CheckItemFieldsValidityPipeline(object):
    """对item进行字段检查"""

    def process_item(self, item, spider):
        rules = spider.config.get("item_field_check_rules")
        if rules:
            flags = [
                load_object(rule['callback'])(item, rule["params"])
                for rule in rules
            ]

            if not all(flags):
                s = json.dumps(dict(item), ensure_ascii=False)
                raise DropItem("item不符合字段校对规则, 丢弃, item如下:{}!".format(s))
        return item