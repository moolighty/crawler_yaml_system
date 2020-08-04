#! /usr/bin/env python3
# -*- coding:utf-8 -*-

"""ks3 操作相关, 具体参考https://docs.ksyun.com/read/latest/65/_book/index.html"""
import logging
import base64
import hmac
import requests
import json

from hashlib import sha1
from scrapy.utils.python import is_listlike
from src.utils.operate_time import get_uc_date_time_str
from src.utils.operate_file import read_file_content_bytes
from src.utils.coding_conversion import url_encode

log = logging.getLogger(__name__)


class Ks3Client:
    """ks3 client类, ks3其中一项根据请求次数来计费"""
    def __init__(self, access_key, secret_key, bucket_name, host_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.host_name = host_name

    def compute_signature(self, http_method, path, date_str,
                          content_md5="", content_type="application/json"):
        # 注意plain_text的参数构造顺序不能错, 否则报错403, forbidden error
        plain_txt = "{}\n{}\n{}\n{}\n{}".format(
            http_method, content_md5, content_type, date_str, path)
        sign = hmac.new(bytes(self.secret_key, encoding="utf8"),
                        bytes(plain_txt, encoding="utf8"),
                        sha1).digest()
        sign = base64.encodebytes(sign).strip()
        sign = sign.decode("utf8")
        return sign

    def compute_authorization(self, http_method, path, date_str,
                              content_md5="", content_type="application/json"):
        """
            签名（Authorization）计算方法
            参考https://docs.ksyun.com/read/latest/65/_book/index.html
        """
        sign = self.compute_signature(http_method, path, date_str, content_md5, content_type)
        authorization = "KSS {}:{}".format(self.access_key, sign)
        return authorization

    def upload_file(self, file_path, file_key, force_override_flag=False, content_type="application/json"):
        """上传文件到Ks3, 注意file_key必须保证唯一, PUT操作"""
        path = self.get_path(file_key)
        if not force_override_flag:  # 是否进行强制覆盖上传, 默认不进行,为False
            if self.is_exist_key(file_key):
                log.warning("文件:{} 已经存在于ks3中,不进行重复上传".format(path))
                return True

        body = read_file_content_bytes(file_path)
        if not body:
            log.warning("读取文件:{}内容失败, 不进行上传文件".format(file_path))
            return False

        return self._upload_body(file_key, body, content_type)

    def upload_item(self, item, file_key, force_override_flag=False, content_type="application/json"):
        """上传item到Ks3, 注意file_key必须保证唯一, PUT操作"""
        path = self.get_path(file_key)
        if not force_override_flag:  # 是否进行强制覆盖上传, 默认不进行,为False
            if self.is_exist_key(file_key):
                log.warning("文件:{} 已经存在于ks3中,不进行重复上传".format(path))
                return True
        s = None
        if is_listlike(item):
            s = json.dumps(item, ensure_ascii=False)
        if isinstance(item, str):
            s = item
        if not s:
            return False
        body = s.encode(encoding='utf-8')
        return self._upload_body(file_key, body, content_type)

    def _upload_body(self, file_key, body, content_type):
        url = self.get_url(file_key)
        headers = self.get_headers("PUT", file_key, content_type)
        response = requests.put(url=url, data=body, headers=headers)
        flag = True if 200 <= response.status_code < 300 else False
        self.response_log(response, flag, "上传body")
        return flag

    def download_file(self, file_key, content_type="application/json"):
        """从Ks3下载文件, 获取文件内容的body, GET操作"""
        url = self.get_url(file_key)
        headers = self.get_headers("GET", file_key, content_type)
        response = requests.get(url=url, headers=headers)
        flag = True if 200 <= response.status_code < 300 else False
        self.response_log(response, flag, "下载文件")
        return response.text if flag else None

    def is_exist_key(self, file_key, content_type="application/json"):
        """判断Ks3是否存在该文件, 或者根据库里是否已经上传的标志来判断, HEAD操作"""
        url = self.get_url(file_key)
        headers = self.get_headers("HEAD", file_key, content_type)
        response = requests.head(url=url, headers=headers)
        flag = True if 200 <= response.status_code <= 300 else False
        # self.response_log(response, flag, "判断文件是否存在")
        return flag

    def delete_file(self, file_key, content_type="application/json"):
        """删除文件, DELETE操作"""
        flag = self.is_exist_key(file_key, content_type)
        if not flag:
            log.warning("文件key:{}不存在bucket:{}中,不进行删除!".format(file_key, self.bucket_name))
            return True
        url = self.get_url(file_key)
        headers = self.get_headers("DELETE", file_key, content_type)
        response = requests.delete(url=url, headers=headers)
        flag = True if 200 <= response.status_code <= 300 else False
        self.response_log(response, flag, "删除文件")
        return flag

    def get_url(self, file_key):
        return "http://{}.{}/{}".format(self.bucket_name, self.host_name, file_key)

    def get_path(self, file_key):
        return "/{}/{}".format(self.bucket_name, file_key)

    def get_headers(self, http_method, file_key, content_type="application/json",
                    content_md5=''):
        date_str = get_uc_date_time_str()
        path = self.get_path(file_key)

        # 这里没有传入content_md5, 这块还需要完善, 这块为核心, 需要验证
        auth = self.compute_authorization(http_method, path, date_str,
                                          content_type=content_type,
                                          content_md5=content_md5)
        headers = {
            "Date": date_str,
            "Content-Type": content_type,
            "Content-MD5": content_md5,
            "Authorization": auth,
        }
        return headers

    def response_log(self, response, flag, msg):
        if not flag:
            log.warning("{} 失败,原因为:{}, 详情为:{}, 状态码为:{}".format(
                msg, response.reason, response.text, response.status_code))

    def get_file_key_by_category(self, category, file_id):
        """
        :param category: listlike or str
        :param file_id: 这里对应mongodb的数据库_id
        :return: file_key str
        """
        if is_listlike(category):
            temp_categories = [c.strip() for c in category if c.strip()]
            dir_path = '/'.join(temp_categories).strip()
        else:
            dir_path = category.strip()
        if not dir_path:
            dir_path = '未知类别'

        # 注意最后需要url encode,因为中文的话需要编码
        file_key = "{}/{}".format(dir_path, file_id)
        file_key = url_encode(file_key)  # url编码是不对/进行编码的
        # 替换特殊字符, 不替换会进行报错403
        file_key = file_key.replace('//', '/%2F')
        file_key = file_key.replace('%7E', '~')
        return file_key

    def get_raw_file_uri(self, file_key):
        return "ks3://{}/{}/{}".format(self.host_name, self.bucket_name, file_key)

    def resolve_file_key_by_uri(self, raw_file_uri):
        """
            resolve file_key to get file key, for example,raw_file_url is like:
            "ks3://ks3-cn-beijing.ksyun.com/corpus/file_key"
            that is: schema://host_name/bucket_name/file_key
        """
        prefix = 'ks3://{}/{}/'.format(self.host_name, self.bucket_name)
        if prefix in raw_file_uri:
            return raw_file_uri[len(prefix):]
        else:
            return None
