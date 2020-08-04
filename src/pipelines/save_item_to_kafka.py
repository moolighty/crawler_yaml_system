#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import logging
import json

from kafka import KafkaProducer
from kafka.errors import KafkaError
from src.utils.coding_conversion import get_md5
from scrapy.exceptions import DropItem

log = logging.getLogger(__name__)


class SaveItemToKafkaPipeline(object):
    """
        发送消息到kafka之前, 先进行检查redis集合中是否存在该_id,
        若不存在，进行消息发送到kafka中,发送成功之后，将该key更新到redis集合中;
        反之，若存在，不进行任何操作，丢弃item.
    """
    producer = None

    def process_item(self, item, spider):
        if not self.producer:
            try:
                self.producer = self.get_producer(spider.env_cls)
            except Exception as e:
                raise DropItem("连接kafka server发生错误, 异常为:{}".format(e))

        try:
            # before sending message to kafka, check key according to redis
            if spider.redis_client.is_key_exist('body_md5_set', item['_id']):
                raise DropItem("消息item 的id为: {}已经存在redis和kafka中， 不进行消息发送!".format(item["_id"]))

            topic_name = spider.env_cls.TOPIC_NAME
            future = self.producer.send(topic_name, key=item['_id'], value=dict(item))
            future.get(timeout=10)

            s = json.dumps(dict(item), ensure_ascii=False)
            # after sending message to kafka, send key to redis
            num1 = spider.redis_client.set_keys('body_md5_set', [item['_id']])
            if num1 != 1:
                log.warning("更新redis set: body_md5_set 失败，item为：{}".format(s))
            url_md5s = [get_md5(url) for url in item['urls']]
            num2 = spider.redis_client.set_keys('url_md5_set', url_md5s)
            if num2 != len(url_md5s):
                log.warning("更新redis set url_md5_set 失败，item为：{}".format(s))

            return item
        except KafkaError as e:
            raise DropItem("连接kafka server发生错误, topic为{}， 异常为:{}".format(topic_name, e))

    def get_producer(self, env_cls):
        bootstrap_servers = env_cls.BOOTSTRAP_SERVERS
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode('utf-8'),
            linger_ms=3000,
            batch_size=65536
        )