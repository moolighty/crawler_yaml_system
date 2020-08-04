#! /usr/bin/env python3
# -*- coding:utf-8 -*-


BOT_NAME = 'crawler_yaml_system'

SPIDER_MODULES = ['src.spiders']

NEWSPIDER_MODULE = 'src.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

# 一定要置为false, 不然很多网站也抓取不了
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 4
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMOUT = 60

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# 重试次数
RETRY_ENABLED = True
RETRY_TIMES = 3

LOG_LEVEL = 'DEBUG'

HTTPPROXY_ENABLED = True
HTTPPROXY_AUTH_ENCODING = 'utf-8'

LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s] [%(process)d:%(processName)s] [%(thread)d:%(threadName)s] ' \
             '[%(filename)s:%(funcName)s:%(lineno)d]] - %(message)s'
