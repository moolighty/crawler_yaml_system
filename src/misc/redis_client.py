#!/usr/bin/env python
# encoding: utf-8
# @Author: Chuanjian Liang
# @Date  : 2019-04-01 09:47:00
"""
    redis客户端, 主要提供两个接口，一个判断key是否存在，一个更新key
"""
import logging
import redis

log = logging.getLogger(__name__)


class RedisClient:

    # 区分读写主要为了加快速度
    reader_redis = None
    writer_redis = None

    def __init__(self, master_host, slave_host, port,
                 password, max_connections):
        self._set_redis_client(master_host, port, password, max_connections, False)
        self._set_redis_client(slave_host, port, password, max_connections, True)

    def set_keys(self, topic_name, values):
        return self.writer_redis.sadd(topic_name, *values)

    def is_key_exist(self, topic_name, value):
        return self.reader_redis.sismember(topic_name, value)

    def _set_redis_client(self, host, port, password, max_connections, is_reader):
        if is_reader and self.reader_redis is None:
            pool = redis.ConnectionPool(
                max_connections=max_connections,
                host=host, port=port, password=password,
                decode_responses=True)
            self.reader_redis = redis.Redis(connection_pool=pool)
        if not is_reader and self.writer_redis is None:
            pool = redis.ConnectionPool(
                max_connections=max_connections,
                host=host, port=port, password=password,
                decode_responses=True
            )
            self.writer_redis = redis.Redis(connection_pool=pool)