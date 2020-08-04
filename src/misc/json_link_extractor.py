#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""增加对json格式的response链接提取的支持, 库SelectJmes需要库jmespath和支持"""

import re
import json
import logging

from scrapy.loader.processors import SelectJmes
from urllib.parse import urljoin
from w3lib.url import canonicalize_url
from w3lib.html import strip_html5_whitespace
from scrapy.link import Link
from scrapy.utils.response import get_base_url
from scrapy.utils.python import unique as unique_list
from scrapy.utils.misc import arg_to_iter
from scrapy.linkextractors import FilteringLinkExtractor, _re_type, IGNORED_EXTENSIONS


log = logging.getLogger(__name__)


class FilteringJsonLinkExtractor(FilteringLinkExtractor):
    """json link 过滤器, 改造基础匹配过滤器,
    进行过滤掉不合法的links, 匹配到合法的links"""

    def __init__(self, link_extractor, allow, deny,
                 allow_domains, deny_domains,
                 canonicalize, deny_extensions):
        del FilteringLinkExtractor._csstranslator

        self.link_extractor = link_extractor

        self.allow_res = [x if isinstance(x, _re_type) else re.compile(x)
                          for x in arg_to_iter(allow)]
        self.deny_res = [x if isinstance(x, _re_type) else re.compile(x)
                         for x in arg_to_iter(deny)]

        self.allow_domains = set(arg_to_iter(allow_domains))
        self.deny_domains = set(arg_to_iter(deny_domains))

        self.canonicalize = canonicalize
        if deny_extensions is None:
            deny_extensions = IGNORED_EXTENSIONS
        self.deny_extensions = {'.' + e for e in arg_to_iter(deny_extensions)}


class JsonParseLinkExtractor(object):
    """json link提取的真正背后执行者, 即分析器"""

    def __init__(self, process=None, unique=True,
                 strip=True, canonicalized=True):
        self.process_attr = process if callable(process) else lambda v: v
        self.unique = unique
        self.strip = strip
        if canonicalized:
            self.link_key = lambda link: link.url
        else:
            self.link_key = lambda link: canonicalize_url(link.url, keep_fragments=True)

    def _extract_links(self, json_path, response):
        # 通过json_path获取具体urls, to add codes here
        try:
            # 通过正则匹配得到具体的json内容信息
            json_re = response.meta.get('json_re', None)
            response_text = response.text
            if json_re:
                mo = re.search(pattern=json_re, string=response_text, flags=re.S | re.M | re.I)
                if mo:
                    response_text = mo.group(1)
            # 因为返回结果为json格式,所以需要先json decode, 有可能发生异常失败
            j = json.loads(response_text, encoding='utf-8')
        except Exception as e:
            log.error(e)
            return []

        json_func = SelectJmes(json_path)
        results = json_func(j)
        if not results:
            log.warning("json_path:{0} 没有在response中没有匹配到相应的links, 退出!".format(json_path))
            return []

        links = []
        base_url = get_base_url(response)
        results = arg_to_iter(results)
        for url_texts in results:
            try:
                url = str(url_texts.get('url', ''))
                if not url:
                    continue
                url = strip_html5_whitespace(url)
                url = urljoin(base_url, url)
                url = self.process_attr(url)
                if not url:
                    continue
                url = urljoin(response.url, url)

                text = url_texts.get('text', '')
                fragment = str(url_texts.get("fragment", ""))
                link = Link(url=url, text=text, fragment=fragment)
                links.append(link)
            except Exception as e:
                log.error(e)

        return self._deduplicate_if_needed(links)

    def _process_links(self, links):
        return self._deduplicate_if_needed(links)

    def _deduplicate_if_needed(self, links):
        if self.unique:
            return unique_list(links, key=self.link_key)
        return links


class JsonLinkExtractor(FilteringJsonLinkExtractor):
    """json link 提取器, 对分析器的包装"""

    def __init__(self, json_paths=(), allow=(), deny=(),
                 allow_domains=(), deny_domains=(), canonicalize=False,
                 unique=True, process_value=None, strip=True,
                 deny_extensions=None):
        lx = JsonParseLinkExtractor(
            unique=unique,
            process=process_value,
            strip=strip,
            canonicalized=canonicalize
        )
        self.json_paths = tuple(arg_to_iter(json_paths))

        super(JsonLinkExtractor, self).__init__(
            link_extractor=lx, allow=allow, deny=deny,
            allow_domains=allow_domains, deny_domains=deny_domains,
            canonicalize=canonicalize, deny_extensions=deny_extensions)

    def extract_links(self, response):
        all_links = []
        for json_path in self.json_paths:
            links = self._extract_links(json_path, response)
            all_links.extend(self._process_links(links))
        return unique_list(all_links)
