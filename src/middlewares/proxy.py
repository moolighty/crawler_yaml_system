# -*- coding: utf-8 -*-
import logging

from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware as BaseProxyMiddleware

log = logging.getLogger(__name__)


class HttpProxyMiddleware(BaseProxyMiddleware):
    proxy_url = 'http://firedraky:z1mkle3k@36.103.242.231:16818'

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy_url
        print(self.proxy_url)
        super().process_request(request, spider)