#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""通用爬虫基类"""

import json
import logging

from scrapy import Request
from scrapy.loader.processors import SelectJmes
from scrapy.spiders import CrawlSpider
from scrapy.http.response import Response
from scrapy.utils.python import is_listlike
from scrapy.utils.misc import load_object
from src.utils.coding_conversion import get_md5
from src.misc.redis_client import RedisClient
from src.misc.rule import Rule

log = logging.getLogger(__name__)


class UniversalBaseSpider(CrawlSpider):
    """通用爬虫类, 若有特殊支持,可以通过继承处理"""
    name = 'universal'

    def __init__(self, config, env_cls, *args, **kwargs):
        """
        配置spider
        :param config: dict 爬虫配置信息
        :param env_cls: EnvironmentConfig 环境变量配置类
        """
        self.link_extractor_rules = config.get("link_extractor_rules")
        self.allowed_domains = config.get('allowed_domains', [])
        self.config = config
        self.env_cls = env_cls  # 对后续的文件保存有用

        self.init_rules()

        # redis这里有两个功能：
        # １.不进行重复抓取，即抓取前会进行request检查;
        # 2. 抓取成功后，对消息是否发送到kafka进行检查，如果已经发送，不进行发送;反之，进行发送.
        self.redis_client = RedisClient(
            env_cls.REDIS_MASTER_HOST, env_cls.REDIS_SLAVE_HOST,
            env_cls.REDIS_PORT, env_cls.REDIS_PASSWORD,
            env_cls.REDIS_MAX_CONNECTIONS
        )

        # 最后放在后面, 父类需要用到rules等属性
        super().__init__(name=self.name, *args, **kwargs)

    def init_rules(self):
        self.rules = []
        nav_link_settings = self.link_extractor_rules.get("nav_link_settings")
        for params in nav_link_settings:
            self.rules.append(Rule(**params))

    def start_requests(self):
        """默认会调用CrawlSpider的parse方法"""
        rules = self.config.get('start_seeds_rules', None)
        request_factory_cls = load_object(rules.get("request_factory_class"))
        req_factory_obj = request_factory_cls()
        depth = int(rules.get("depth"))
        check_before_request_flag = rules.get("check_before_request_flag", False)

        # 第一种情况, 默认配置的urls集合
        category_urls = rules.get("category_urls")
        if isinstance(category_urls, dict) and category_urls:
            for category, urls in category_urls.items():
                if is_listlike(urls):
                    if check_before_request_flag:
                        urls = [url for url in urls
                                if not self.check_url_in_redis_set(url)]
                    if not urls:
                        continue
                    for request in req_factory_obj.batch_make_requests(
                            spider=self, depth=depth,
                            link_or_url_list=urls,
                            meta={'category': category}):
                        yield request

        # 第二种情况, 通过函数泛化
        callback_urls = rules.get("callback_urls")
        if isinstance(callback_urls, dict) and callback_urls:
            for category, callback_url_infos in callback_urls.items():
                for infos in callback_url_infos:
                    callback = infos.get('callback').strip()
                    if not callback:
                        continue
                    if isinstance(callback, str):
                        callback = load_object(callback)
                    params = infos.get('params')
                    if callable(callback) and isinstance(params, dict):
                        urls_or_requests = callback(**params)
                        if check_before_request_flag:
                            urls_or_requests = [
                                e for e in urls_or_requests if not self.check_url_in_redis_set(e)
                            ]
                        if not urls_or_requests:
                            continue
                        urls = [e for e in urls_or_requests if isinstance(e , str) and e.startswith('http')]
                        for request in req_factory_obj.batch_make_requests(
                                spider=self, depth=depth,
                                link_or_url_list=urls,
                                meta={'category': category}):
                            yield request
                        requests = [e for e in urls_or_requests if isinstance(e, Request)]
                        for request in requests:
                            yield request

    def parse_start_url(self, response):
        """
            若初始种子对应的页面就是详情页,
            则直接调用parse_item方法,
            反之调用默认的父类方法
        """
        rules = self.config.get('start_seeds_rules')
        if rules.get("detail_page_flag"):
            for item in self.parse_item(response):
                yield item
        return []

    def _build_request(self, rule, link):
        """
        :param rule: 对应self._rules的下标
        :param link: Link对象
        :return: 返回request对象
        """
        rule_obj = self._rules[rule]
        request_factory_cls = rule_obj.request_factory_class
        req_factory_obj = request_factory_cls()
        depth = rule_obj.depth
        # 根据工厂类制作request
        request = req_factory_obj.make_request(
            spider=self, depth=depth, link_or_url=link)
        request.callback = self._response_downloaded
        # must add rule index to the meta
        request.meta.update(rule=rule, link_text=link.text, fragment=link.fragment)
        return request

    def _requests_to_follow(self, response):
        """
        :param response: 注意response必须要有depth和category参数
        :return:
        """
        if not response or not isinstance(response, Response):
            return

        self.set_response_encoding(response)

        category = response.meta['category']
        depth = self.rules[response.meta['rule']].depth if 'rule' in response.meta else 0
        if not response.meta.get('next_page_flag', False):
            depth += 1  # 不是下一页标志,进入下一层; 反之, depth保持不变

        seen = set()
        for n, rule in enumerate(self._rules):
            # 选择符合条件的rule, 可能有多个
            flag = rule.depth == depth and category == rule.category
            if not flag:
                continue

            check_before_request_flag = rule.meta.get('check_before_request_flag', False)
            next_page_flag = rule.meta.get('next_page_flag', False)
            json_re = rule.meta.get('json_re', None)
            if json_re:
                response.meta.update(json_re=json_re)

            links = [lnk for lnk in rule.link_extractor.extract_links(response) if lnk not in seen]
            if links and rule.process_links and callable(rule.process_links):
                links = rule.process_links(links)
            if check_before_request_flag:
                links = [link for link in links if not self.check_url_in_redis_set(link.url)]
            if not links:
                continue

            for link in links:
                seen.add(link)
                # 构造请求
                request = self._build_request(n, link)
                request.meta.update(category=rule.category)
                request.meta.update(next_page_flag=next_page_flag)
                dont_filter = rule.meta.get('dont_filter', False)
                request.dont_filter = dont_filter

                yield rule.process_request(request)

    def parse_item(self, response):
        """
            解析详情页,得到所有的item,这也是爬取网站的最终目的,
            爬取的产物就是得到结构化字段, 即item,
            :param response 的meta字段必须含有category字段
        """
        if not response or not isinstance(response, Response):
            return

        if not hasattr(response, 'meta') or 'category' not in response.meta:
            return

        self.set_response_encoding(response)
        category = response.meta['category']

        item_extractor_rules = self.config.get("item_extractor_rules")
        loaders = self.populate_item_loaders(response, item_extractor_rules, category)
        for loader in loaders:
            item = loader.load_item()
            yield item

    def populate_item_loaders(self, response, item_extractor_rules, category):
        """
            :param response 的meta字段必须含有category字段
            填充item字段信息, 得到item loaders
        """
        loaders = []
        try:
            item_cls = load_object(item_extractor_rules.get("item_class"))
            loader_cls = load_object(item_extractor_rules.get("item_loader_class"))

            category_cases_relations = item_extractor_rules.get("category_cases_relations")
            if category not in category_cases_relations:
                log.warning("item_extractor_rules中没有相应类别：{}的特征提取器".format(category))
                return
            case_types = category_cases_relations[category]

            # 响应结果为xml(包含html)格式的item解析的方式
            extractor_type = item_extractor_rules.get('extractor_type')
            if extractor_type not in ['xml', 'json']:
                log.warning("特征提取器既不是xml格式,也不是json格式,请检查配置文件!")
                return []

            get_loader_method = self._get_xml_loaders if extractor_type == 'xml' else self._get_json_loaders
            field_extractors = item_extractor_rules.get("{}_field_extractors".format(extractor_type))
            for case_type in case_types:
                field_extractor = field_extractors.get(case_type, {})
                if not field_extractor:
                    log.warning("没有找打对应类型：{}的特征提取器".format(extractor_type))
                    continue
                temp_loaders = get_loader_method(response, field_extractor, item_cls, loader_cls)
                loaders += temp_loaders

        except Exception as e:
            log.error("装载清洗得到item时, 发生异常, 原因为:{}".format(e))

        return loaders

    def set_response_encoding(self, response):
        """设置编码,防止乱码"""
        try:
            if response.request.encoding:  # 以我们传参的编码为最高优先级
                response._encoding = response.request.encoding
                response._cached_ubody = None
        except Exception as e:
            log.error(e)

    def check_url_in_redis_set(self, url_or_request):
        if isinstance(url_or_request, str):
            url = url_or_request
        if isinstance(url_or_request, Request):
            url = url_or_request.url

        url = url.strip()
        if not url:
            return True

        # 跟计算文件id的方法保持一致，url必须数组形式计算md5
        url_md5 = get_md5(url)
        flag = self.redis_client.is_key_exist('url_md5_set', url_md5)
        if flag:
            log.debug("url:{}对应的md5:{}已经在redis set中，不进行再次抓取！".format(url, url_md5))
        return flag

    def _get_xml_loaders(self, response, field_extractor, item_cls, loader_cls):
        """对xml(html)格式的响应结果进行解析"""
        loader = loader_cls(item=item_cls(), response=response)
        for field_name, extractors in field_extractor.items():
            for extractor in extractors:
                type_ = extractor.get('type')
                # 可能是xpath路径, css选择器,也可能是字段属性名称等
                param = extractor.get('param')
                regex = extractor.get('regex')
                regex = {'re': regex} if regex else {'re': None}

                if type_ == "xpath":
                    loader.add_xpath(field_name, param, **regex)
                elif type_ == "css":
                    loader.add_css(field_name, param, **regex)
                elif type_ == "response_attr":
                    loader.add_value(field_name, getattr(response, param, None), **regex)
                elif type_ == "response_meta_attr":
                    loader.add_value(field_name, response.meta.get(param, None), **regex)
                elif type_ == "value":  # 直接赋值
                    loader.add_value(field_name, param)
                else:
                    log.warning("type:{} 取值不在规定的几种方式之中, 请检查配置文件!".format(type_))

        return [loader]

    def _get_json_loaders(self, response, field_extractor, item_cls, loader_cls):
        """对json格式进行解析提取item"""
        def _generate_loader(d):
            if not isinstance(d, dict):
                log.warning("元素不是字典类型，请检查json path的配置语法！")
                return None
            loader = loader_cls(item=item_cls())
            for k, v in d.items():
                loader.add_value(k, v)
            return loader

        json_path = field_extractor["json_path"]
        encoding = field_extractor["encoding"]
        jn = json.loads(response.text, encoding=encoding)
        # 若获取的结果一个list, 则list的元素都是具体的item了;
        # 若获取的结果是一个dict, 则直接是一个item了
        results = SelectJmes(json_path=json_path)(jn)

        if isinstance(results, dict):
            results = [results]
        if not isinstance(results, list):
            log.warning("json 查询语言配置格式不对，请核查json_path:{}".format(json_path))

        loaders = []
        for d in results:
            if not d:
                continue
            temp_loader = _generate_loader(d)
            if temp_loader:
                loaders.append(temp_loader)

        return loaders
