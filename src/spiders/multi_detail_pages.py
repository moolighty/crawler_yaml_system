#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""multi detail pages base spider"""

import logging

from scrapy.utils.misc import load_object
from . import UniversalBaseSpider

log = logging.getLogger(__name__)


class MultiDetailPagesSpider(UniversalBaseSpider):

    name = 'multi_detail_pages'

    def parse_item(self, response):
        self.set_response_encoding(response)

        rules = self.config["link_extractor_rules"]["details_next_page_settings"]
        # if not next page flag set, just return item
        if not rules.get("next_page_flag", False):
            yield next(super().parse_item(response))

        # get next page, and merge corresponding fields
        else:
            merge_fields = rules["merge_fields"]
            # get history page item
            item = response.meta.get('item', None)
            if item is None:
                # record first page item
                item = next(super().parse_item(response))
                for field in merge_fields:
                    if field not in item:
                        # 有可能字段内容为空，需要跳过，不然报错，比如body,
                        # 参考网页https://www.liuxue86.com/a/1824743_2.html
                        continue
                    if not isinstance(item.get(field), list):
                        item[field] = [item[field]]
            else:
                # merge all fields that need to be merged
                cur_item = next(super().parse_item(response))
                for field in merge_fields:
                    if field not in cur_item:
                        # 有可能字段内容为空，需要跳过，不然报错，比如body,
                        # 参考网页https://www.liuxue86.com/a/1824743_2.html
                        continue
                    if isinstance(cur_item[field], list):
                        item[field].extend(cur_item[field])
                    else:
                        item[field].append(cur_item[field])
            # get next page request
            next_req = self._get_next_page_request(response, rules)
            # just return item if no next page request got
            if not next_req:
                if 'body' in item and isinstance(item['body'], list):
                    item['body'] = '\n'.join(item['body'])
                yield item
            # regard current item as history item, and return next page request
            else:
                next_req.meta.update(item=item)
                next_req.callback = self.parse_item
                yield next_req

    def _get_next_page_request(self, response, rules):
        extractors = rules["extractors"]
        for rule in extractors:
            xpath = rule["xpath"]
            regex = rule['regex']
            # get url by xpath and re configs
            url = response.xpath(xpath).re_first(regex) if regex else response.xpath(xpath).extract_first()
            # maybe multi rules be created to parse next page url
            if not url or not isinstance(url, str) or not url.strip():
                continue
            request_factory_cls = load_object(rule["request_factory_class"])
            req_factory_obj = request_factory_cls()
            # generate next page request and return
            return req_factory_obj.make_request(
                spider=self,
                depth=rule["depth"],
                link_or_url=response.urljoin(url).strip(),
                meta=response.meta)
        # if no next page request, return None
        return None
