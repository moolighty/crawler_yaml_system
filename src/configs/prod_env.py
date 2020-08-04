#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    环境配置
"""


class ProductEnviromentConfig:
    DATA_PATH = 'datas.out'
    LOG_PATH = 'logs'
    LOG_LEVEL = 'INFO'

    # kafka配置
    BOOTSTRAP_SERVERS = ['ip:port']
    TOPIC_NAME = "crawler_official_document"

    # redis配置
    REDIS_MASTER_HOST = 'ip'
    REDIS_SLAVE_HOST = 'port'
    REDIS_PORT = 6379
    REDIS_MAX_CONNECTIONS = 4000
    REDIS_PASSWORD = None
