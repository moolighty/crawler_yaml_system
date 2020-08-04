#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import logging

from scrapy import Field, Item
from src.utils.operate_time import get_now_str
from src.utils.operate_html import get_scheme_domain
log = logging.getLogger(__name__)


class BaseItem(Item):
    """基类item定义"""
    _id = Field()      # 主要用于去重, 主要根据url求取md5值, 为str类型
    urls = Field()     # 请求地址, 为数组类型
    site_domain = Field()  # 网站域名地址
    title = Field()    # 标题, 为str类型
    body = Field()     # 正文, 为str类型
    abstract = Field()  # 摘要
    category = Field()  # 网站文章目录类别
    tags = Field()      # 自定义产品类别标签
    published_at = Field()  # 文章发布时间
    editors = Field()   # 文章作者
    organization_name = Field()  # 文章发布机构名称
    created_at = Field()    # 创建时间
    email = Field()

    @classmethod
    def init_item(cls):
        item = cls()
        item['_id'] = ''
        item['urls'] = []
        item['site_domain'] = ''  # site_domain需要更新, initialize那里
        item['title'] = ''
        item['body'] = ''
        item['abstract'] = ''
        item['category'] = []
        item['tags'] = []
        item['published_at'] = ''
        item['editors'] = []
        item['organization_name'] = ''  # 机构名称需要更新
        item['created_at'] = get_now_str()
        item['email'] = ''

        return item

    @classmethod
    def set_site_domain(cls, item):
        try:
            if 'site_domain' not in item or not item['site_domain'] and item['urls']:
                item['site_domain'] = get_scheme_domain(item['urls'][0])
        except Exception as e:
            log.error("设置site_domain发生异常, 原因为:{}".format(e))
        return item

    @classmethod
    def set_category(cls, item):
        category = item['category']
        if not category:
            return item

        if not isinstance(category, list):
            category = [category]
        category = [e.strip() for e in category if e.strip()]
        category = [e[:-1] if e.endswith('/') else e for e in category]

        organization_name = item['organization_name']
        if organization_name and item['category'] and item['category'][0] in organization_name:
            category = item['category'][1:]
        item['category'] = category

        return item