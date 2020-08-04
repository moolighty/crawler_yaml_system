#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""html相关操作"""

import re
import logging
import json
import requests

from urllib.parse import urlparse
from pyquery import PyQuery as pq
from scrapy.http.response.html import HtmlResponse
from . import ALL_PUNCTUATIONS

log = logging.getLogger(__name__)


def replace_repeat_characters(s, search_char='\n', replace_chars=None, pattern=None):
    """替换连续重复出现的search_char"""
    if not pattern:
        pattern = search_char + "+"
    if not replace_chars:
        replace_chars = search_char
    return re.sub(pattern, replace_chars, s)


def strip_whitespace(s):
    return re.sub('\s+', '', s)


def strip_punctuation(s):
    """去掉所有的符号"""
    punctuations = re.escape(ALL_PUNCTUATIONS)
    pattern = "[{}]+".format(punctuations)
    return re.sub(pattern=pattern, repl='', string=s)


def strip_whitespace_punctuation(s):
    punctuations = re.escape(ALL_PUNCTUATIONS)
    pattern = "[\s{}]+".format(punctuations)
    return re.sub(pattern=pattern, repl='', string=s)


def get_plain_text(html_content, css_selector='',
                   exclusive_selectors=('script', 'style', 'img', 'video')):
    """
    去掉html页面的标签,得到纯文本
    :param html_content: 页面内容
    :param css_selector: 需要定位的css选择器
    :param exclusive_selectors: 排除的css选择器
    :return: 得到需要内容的纯文本
    """
    if not html_content or not html_content.strip():
        return ''
    try:
        doc = pq(html_content)
        if css_selector:
            doc = doc(css_selector)
        for s in exclusive_selectors:
            doc.find(s).remove()
        return replace_repeat_characters(doc.text().strip())
    except Exception as e:
        logging.exception(e)
        return ''


def get_all_chinese_phrase_list(s):
    """得到所有的中文词汇"""
    return re.findall('[\u4E00-\u9FA5]+', s)


def get_scheme_domain(url):
    result = urlparse(url)
    domain = result.netloc.strip()
    scheme = result.scheme.strip()
    # 去掉端口号
    return "{}://{}".format(scheme, domain)


def split_cookie_to_dict(cookie):
    """将cookie字符串变为字典形式"""
    try:
        l = cookie.split(';')
        return {e.split('=')[0]: e.split('=')[1] for e in l}
    except Exception as e:
        log.exception(e)
    return None


def get_category(response, category_map_relations,
                 default_category='未知类别'):
    """得到类别"""
    try:
        if 'category' in response.meta:
            return response.meta['category']

        url = response.url
        for key, category in category_map_relations.items():
            if key in url:
                return category
    except Exception as e:
        log.exception(e)

    return default_category


def build_repsonse(body, url='', headers={}, request=None):
    """构造HtmlResponse对象"""
    if isinstance(body, bytes):
        bs = body
    elif isinstance(body, str):
        bs = body.encode(encoding='utf-8')
    else:
        bs = json.dumps(body).encode('utf-8')
    return HtmlResponse(encoding='utf-8', url=url,
                        headers=headers, body=bs, request=request)


def download(url, method='GET', headers={}, data=None):
    return requests.request(method=method, url=url, headers=headers, data=data)


def check_url_validity(url, length=10):
    url = url.strip()
    if url.startswith('http://') or \
            url.startswith('https://') or len(url) > length:
        return True
    return False
