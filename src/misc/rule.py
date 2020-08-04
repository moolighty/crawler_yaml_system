#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from scrapy.spiders.crawl import Rule as BaseRule, identity
from scrapy.utils.misc import load_object


class Rule(BaseRule):
    """规则定义拓展, 增加导航深度和request生成的支持"""

    def __init__(self, depth, request_factory_class,
                 link_extractor_settings, category, meta={},
                 callback=None, cb_kwargs=None, follow=None,
                 process_links=None, process_request=None):
        cls = link_extractor_settings['link_extractor_class']
        link_extractor_class = load_object(cls) if isinstance(cls, str) else cls
        link_extractor = link_extractor_class(**link_extractor_settings['params'])

        process_links = load_object(process_links) if isinstance(process_links, str) else process_links
        process_request = load_object(process_request) if isinstance(process_request, str) else process_request
        if not process_request:
            process_request = identity

        super(Rule, self).__init__(
            link_extractor=link_extractor,
            callback=callback,
            cb_kwargs=cb_kwargs,
            follow=follow,
            process_links=process_links,
            process_request=process_request
        )
        self.depth = depth
        self.category = category
        self.meta = meta
        self.request_factory_class = load_object(request_factory_class) \
            if isinstance(request_factory_class, str) else request_factory_class
