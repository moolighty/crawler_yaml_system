#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import json

from src.utils.operate_file import write_item_to_file, exist_file
from scrapy.exceptions import DropItem

log = logging.getLogger(__name__)


class SaveFileToLocalePipeline(object):
    """将item存入本地文件"""
    def process_item(self, item, spider):
        s = json.dumps(dict(item), ensure_ascii=False)
        local_file_path = self.compute_file_path(item, spider)
        # 覆盖文件
        if exist_file(local_file_path):
            return item

        flag = write_item_to_file(local_file_path, dict(item))
        if flag:
            return item
        else:
            raise DropItem("写入item:{} 到文件{}失败".format(s, local_file_path))

    def compute_file_path(self, item, spider):
        try:
            file_rules = spider.config.get("item_file_rules")
            file_suffix = file_rules.get("file_suffix")
            save_dir = self.get_save_dir(spider, file_rules, item)
            file_path = "{}/{}{}".format(save_dir, item["_id"], file_suffix)
            return file_path
        except Exception as e:
            log.error("计算文件保存路径发生异常,异常原因如下:{}".format(e))
        return None

    def get_save_dir(self, spider, file_rules, item):
        """得到保存的目录"""
        data_path = spider.env_cls.DATA_PATH
        parent_dir = file_rules.get("parent_dir").strip()
        if not parent_dir:
            return data_path
        return "{}/{}".format(data_path, parent_dir)


class SaveFileToLocaleByCategoryPipeline(SaveFileToLocalePipeline):
    """将item根据类别分别存储到不同的本地目录中"""
    def get_save_dir(self, spider, file_rules, item):
        data_path = spider.env_cls.DATA_PATH
        parent_dir = file_rules.get("parent_dir").strip()
        organization_name = item['organization_name']
        path = organization_name
        # 避免目录重复
        if parent_dir and parent_dir not in organization_name:
            path = "{}/{}".format(parent_dir, organization_name)
        save_dir = "{}/{}".format(data_path, path)

        category = "/".join(item['category'])

        return "{}/{}".format(save_dir, category) if category else save_dir
