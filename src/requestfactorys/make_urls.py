#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from src.utils.coding_conversion import url_encode
from src.utils.operate_time import get_now_timestamp_millisecond_str


def get_urls_by_page(urls=[], url_format=None, start_page_id=0, end_page_id=0):
    """根据起始id和结束id, 以及初始urls集合,来生成要urls集合"""
    if url_format:
        for page in range(start_page_id, end_page_id + 1):
            urls.append(url_format.format(page))
    return urls


def get_urls_by_page_ranges(urls=[], start_range_id=0, end_range_id=0, url_format=None, start_page_id=0, end_page_id=0):
    for range_id in range(start_range_id, end_range_id):
        for page in range(start_page_id, end_page_id + 1):
            urls.append(url_format.format(range_id, page))
    return urls


def get_urls_by_list_page(url_infos=[], urls=[]):
    """根据列表生成urls"""
    for info in url_infos:
        urls = get_urls_by_page(urls=urls, **info)
    return urls


def get_urls_by_now_millisecond(urls=[], url_format=None):
    """根据时间生成urls"""
    if url_format:
        urls.append(url_format.format(get_now_timestamp_millisecond_str()))
    return urls


def get_urls_by_query_params(url_format=None, query_params=[], urls=[]):
    """根据查询参数生成urls"""
    if url_format:
        for query_param in query_params:
            urls.append(url_format.format(url_encode(query_param)))
    return urls


def get_urls_by_categories(urls=[], url_format=None, categories=[]):
    """根据起始id和结束id, 以及初始urls集合,来生成要urls集合"""
    if url_format:
        for category in categories:
            urls.append(url_format.format(category))
    return urls