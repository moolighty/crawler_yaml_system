#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import re

from src.loaders import BaseItemLoader, get_plain_text, MapCompose


def _extract_body(body_content):
    s = get_plain_text(
        html_content=body_content,
        css_selector="",
        exclusive_selectors=(
            "script", "style", 'img', 'video',
            'div#ipage', 'p > strong:first-child',
            'p.copy1'
        )
    )
    pattern = "\s*.*?(文秘网|QQ：|小编为各位|小编为大家|小编寄语|请大家参阅" \
              "|优质的一对一服务｜以下范文|供您参考｜企业QQ|原创文章定制服务" \
              "|在线客服|咨询服务|小编希望|定制写作联系电话)+.*?[。！\s]*\n"

    s = re.sub(pattern=pattern, repl='', string=s).strip()
    pattern = "(本文网址|文章地址)：https?://www\.91wenmi\.com/wenmi/.*/\d+\.html"
    return re.sub(pattern, '', s).strip()


class WenmiItemLoader(BaseItemLoader):

    body_in = MapCompose(_extract_body)
    tags_in = MapCompose(lambda tag: tag if tag != '文秘网' else None)
