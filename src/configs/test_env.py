#!/usr/bin/env python
# encoding: utf-8


class TestEnviromentConfig:
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