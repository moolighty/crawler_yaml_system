#! /usr/bin/env python3
# -*- coding:utf-8 -*-


class UniversalBasePipeline(object):

    def process_item(self, item, spider):
        # 什么都不做,原样返回
        return item
