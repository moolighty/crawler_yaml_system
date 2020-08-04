#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""常用通用item loaders定义, 主要在这里定义一些通用的方法"""

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Identity, Join
from src.utils.operate_html import get_plain_text


class InputStripItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)


class OutputTaskFirstItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class BaseItemLoader(InputStripItemLoader, OutputTaskFirstItemLoader):
    title_in = MapCompose(get_plain_text)
    body_in = MapCompose(get_plain_text, str.strip)

    published_at_in = Join()

    abstract_in = MapCompose(get_plain_text, str.strip)
    abstract_out = Join()

    urls_out = Identity()
    tags_out = Identity()
    editors_out = Identity()
    category_out = Identity()