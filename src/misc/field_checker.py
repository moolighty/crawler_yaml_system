#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from scrapy.utils.python import is_listlike, flatten


def _check_field_in_item(item, field_name):
    if field_name not in item:
        return False

    if isinstance(item[field_name], str):
        item[field_name] = item[field_name].strip()

    if not item[field_name]:
        return False

    return True


def check_field_list_in_item(item, field_params=[]):
    flags = [
        _check_field_in_item(item, field_name)
        for field_name in field_params
    ]
    return all(flags)


def _check_field_len_validity(item, field_name, length=1):
    if not _check_field_in_item(item, field_name):
        return False
    str_or_list = item[field_name]
    if not str_or_list:
        return False
    elif isinstance(str_or_list, str):
        return len(str_or_list.strip()) >= length
    elif is_listlike(str_or_list):
        s = ''.join(flatten(str_or_list)).strip()
        return len(s) >= length
    return False


def check_field_list_len_validity(item, field_params={}):
    flags = [
        _check_field_len_validity(item, field_name, length)
        for field_name, length in field_params.items()
    ]
    return all(flags)
