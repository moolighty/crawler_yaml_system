#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    环境配置
"""


class DevelopEnvironmentConfig:
    DATA_PATH = 'datas.out'
    LOG_PATH = 'logs'
    LOG_LEVEL = 'DEBUG'

    # kafka配置
    BOOTSTRAP_SERVERS = ['127.0.0.1:9092']
    TOPIC_NAME = "crawler_official_document"

    # redis配置
    REDIS_MASTER_HOST = '127.0.0.1'  # 本地redis服务
    REDIS_SLAVE_HOST = '127.0.0.1'

    REDIS_PORT = 6379
    REDIS_MAX_CONNECTIONS = 100
    REDIS_PASSWORD = None
