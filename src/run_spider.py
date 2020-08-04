#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import yaml
import sys
import os

from os.path import join, abspath, dirname
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.utils.operate_file import exist_file
from src.utils.operate_time import get_now_timestamp_second_str
from src.configs.prod_env import ProductEnviromentConfig
from src.configs.dev_env import DevelopEnvironmentConfig
from src.configs.test_env import TestEnviromentConfig

log = logging.getLogger(__name__)
SPIDER_YAMLS_DIR = abspath(join(dirname(__file__), 'spider_yamls'))


def run(name, env):
    """
        根据src/spider_yamls目录下面的配置文件名称来进行启动爬虫程序,
        这里的name指的是配置文件名称,不带.yaml后缀, 比如:example_xml.yaml,
    @:param flag 0:表示开发测试环境 1:表示线上环境
    """
    spider_yaml_file = "{}/{}.yaml".format(SPIDER_YAMLS_DIR, name)
    if not exist_file(spider_yaml_file):
        log.error("该网站对应的爬虫文件：{} 不存在, 退出!".format(spider_yaml_file))
        return
    with open(spider_yaml_file, encoding='utf-8') as f:
        spider_yaml_configs = yaml.load(f)

    # 区别开发环境和生成环境创建数据和日志目录,
    if env == "test":
        env_cls = TestEnviromentConfig
    elif env == "prod":
        env_cls = ProductEnviromentConfig
    else:
        env_cls = DevelopEnvironmentConfig

    # 爬虫配置
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    custom_settings = spider_yaml_configs.get('custom_settings', {})
    settings.update(custom_settings)

    # 日志文件
    log_file_name = settings["LOG_FILE"] if settings.get("LOG_FILE") else name
    log_file = "logs/{}_{}.log".format(log_file_name, get_now_timestamp_second_str())
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    settings["LOG_FILE"] = log_file

    # 初始化和启动crawler进程
    spider_name = spider_yaml_configs.get("spider_name", 'universal')
    process = CrawlerProcess(settings)
    process.crawl(spider_name, **{
        'config': spider_yaml_configs,
        'env_cls': env_cls,
    })
    process.start()


if __name__ == "__main__":
    yaml_prefix = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 1 else "dev"
    run(yaml_prefix, env)
