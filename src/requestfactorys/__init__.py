#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""Request制作工厂类, 应用工厂方法和模板方法两个设计模式"""
import logging
import copy
import json

from abc import ABCMeta, abstractmethod
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest
from scrapy.link import Link
from scrapy.utils.python import is_listlike
from src.utils.operate_html import check_url_validity
from src.configs.common import headers as base_headers

log = logging.getLogger(__name__)


class BaseRequestFactory(metaclass=ABCMeta):
    """抽象Request制作工厂"""

    def batch_make_requests(self, spider, depth=0, link_or_url_list=[], meta={}):
        if is_listlike(link_or_url_list) and link_or_url_list:
            for link_or_url in link_or_url_list:
                yield self.make_request(spider, depth, link_or_url, meta)

    def make_request(self, spider, depth=0, link_or_url='', meta={}):
        """spider 的实例对象"""
        try:
            if link_or_url:
                # 第一步得到url和对应的链接文本
                url, link_text = self.get_request_url_and_text(link_or_url)
                if not url:
                    log.warning("{} 对应的url不合法, 制作Request失败!".format(link_or_url))
                    return None

                # 第二步得到构造request的参数参数
                params = self.get_request_params(spider, depth, url, link_text, meta)

                # 第三步根据上面两步制作request对象
                return self.get_request_object(params)
        except Exception as e:
            log.error("生成request时发生异常, 原因为:{}".format(e))

        return None

    @abstractmethod
    def get_request_params(self, spider, depth, url, link_text='', meta={}):
        """
        :param spider 应的spider实例对象
        :param depth 对应的深度
        :param url: 待请求的url
        :param link_text: 请求url对应的锚文本
        :param meta:{}
        :return: 返回构造Request对象需要的具体参数
        """
        pass

    def get_request_object(self, params):
        """构造request对象"""
        formdata = params.get('formdata', {})
        if formdata:
            if isinstance(formdata, dict):
                return FormRequest(**params)
            else:
                s = json.dumps(formdata, ensure_ascii=False)
                log.warning("formdata:{}格式不对, 无法制造FormRequest对象".format(s))
                return None
        else:
            temp_params = copy.deepcopy(params)
            if 'formdata' in temp_params:
                del temp_params['formdata']
            return Request(**temp_params)

    def get_request_url_and_text(self, link_or_url):
        """得到链接和链接文本"""
        if isinstance(link_or_url, Link):
            url = link_or_url.url.strip()
            if check_url_validity(url):
                return url, link_or_url.text.strip()
        if isinstance(link_or_url, str):
            url = link_or_url.strip()
            if check_url_validity(url):
                return link_or_url.strip(), ''
        return None, ''


class DepthRequestFactory(BaseRequestFactory):
    """根据网站链接深度来制作Request对象"""

    def get_request_params(self, spider, depth, url, link_text='', meta={}):
        """
        :param spider 对应的spider实例对象
        :param depth 对应的深度
        :param url: 待请求的url
        :param link_text: 请求url对应的锚文本
        :param meta:{} 需要通过reqeust 传送的附带信息, depth必须要传送的
        :return: 返回构造Request对象需要的具体参数
        """
        # depth一定要设置,根据depth来选择提取链接的Rule, 这一步很重要
        # 根据配置的规则更新params
        conf = spider.config
        request_params_rules = conf.get("request_params_rules")
        headers = copy.deepcopy(base_headers)
        headers.update(request_params_rules.get("common_headers"))
        rules = self._find_reqeust_params_rules(depth, request_params_rules)
        if not rules:
            return {
                'url': url,
                'method': 'GET',  # 除了get的请求,还有post请求
                'headers': headers,  # 该headers与common_request_headers互为补充, 不过该优先级最高
                'body': '',  # 字符串类型,对应要传送的数据data, 一般为post请求要传送的数据,
                'cookies': {},  # 字典类型,需要传入的cookies信息, 也可以headers字段传入
                'meta': meta,  # 额外要传输的元数据,即复制到response的meta中
                'dont_filter': False,  # 默认情况下是要进行过滤
                'encoding': 'utf-8',  # 网页编码
                'formdata': {},  # 字典类型
            }
        # 因为是dict, 即引用类型, 必须深拷贝, 不然改动params会改动spider.config里的状态,
        # 从而影响后面的操作, 最后不要改动全局配置,否则会有意想不到的逻辑错误
        params = copy.deepcopy(rules.get("params"))
        params['url'] = url
        params['meta'].update(meta)
        return self._update_params(headers, params)

    def _find_reqeust_params_rules(self, depth, request_params_rules):
        try:
            depth_headers = request_params_rules.get("depth_headers")
            for rules in depth_headers:
                # 优先选择第一个出现的规则
                if depth in rules.get("depths"):
                    return rules
        except Exception as e:
            log.error("在爬虫配置文件没有深度为:{} 的头部配置, 异常原因如下:{}".format(depth, e))
        return None

    def _update_params(self, headers, params):
        """注意不要直接修改headers, 因为python是传引用,修改会引起公共的headers变化"""
        temp_headers = copy.deepcopy(headers)

        if 'cookie' in temp_headers:
            temp_headers['Cookie'] = temp_headers['cookie']
            del temp_headers['cookie']
        if 'cookies' in params and params['cookies'] and 'Cookie' in temp_headers:
            del temp_headers['Cookie']
        if 'cookies' in params and not params['cookies']:
            del params['cookies']

        # 以params的cookie优先级最高
        if params['headers'] and isinstance(params['headers'], dict):
            temp_headers.update(params['headers'])
        params['headers'] = temp_headers
        return params
