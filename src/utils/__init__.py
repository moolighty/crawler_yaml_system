#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from string import punctuation, whitespace, ascii_letters, \
    ascii_lowercase, ascii_uppercase, digits, printable

ENGLISH_PUNCTUATION = punctuation
ENGLISH_WHITESPACE = whitespace
ENGLISH_LOWER_ASCII = ascii_lowercase
ENGLISH_UPPER_ASCII = ascii_uppercase
ENGLISH_ASCII = ascii_letters
ENGLISH_DIGITS = digits
ENGLISH_PRINTABLE = printable

SPECIAL_PUNCTUATION = r"""
    。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨…
    .¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴﹟#
    ﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<＿_-\
    ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕
    {}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼
    ○◇□△▽▷◁☆♤♡♢♧●◆■▲▼▶◀★♠♥♦♣☼☺◘☏☜◐☽♀☑√✔㏂☀
    ☻◙☎☞◑☾♂☒×✘㏘✎✐▁▂▃▄▅▆▇█⊙◎✉☯♨۞✄☢☣➴➵卍卐✈✁
    〠〄♝♞◕†‡¬￢✌☭❂☪☃☂❦❧✲❈❉*✪☉⊕Θ⊿▫◈▣❤✙۩✖✚
    ♩♪♫♬¶♭♯∮‖§Ψ☠⊱⋛⋌⋚⊰⊹▪•‥…❀๑㊤㊥㊦㊧㊨㊚㊛㊣
    ㊙㈜№㏇㈱㍿㉿®℗©™℡✍曱甴囍▧▤▨▥▩▦▣▓∷▒░☌╱╲▁▏
    ↖↗↑←↔◤◥☍╲╱▔▕↙↘↓→↕◣◢☋➟➡➢➣➤➥➦➧➨➚➘➙➛➜➝➞➸
    ♐➲➳⏎➴➵➶➷➸➹➺➻➼➽←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦
    ↧↨➫➬➩➪➭➮➯➱↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃
    ⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪
"""

MATH_PUNCTUATION = r"""
    ＋－×÷﹢﹣±／＝≈≡≠∧∨∑∏∪∩∈⊙⌒⊥∥∠∽≌＜＞≤≥≮≯∧∨√
    ﹙﹚[]﹛﹜∫∮∝∞⊙∏º¹²³⁴ⁿ₁₂₃₄·∶½⅓⅔¼¾⅛⅜⅝⅞∴∵∷α
    βγδεζηθικλμνξοπρστυφχψω％‰℅°℃℉′″￠〒¤○㎎㎏
    ㎜㎝㎞㎡㎥㏄㏎mlmol㏕Pa＄￡￥㏒㏑
"""

ALL_PUNCTUATIONS = ENGLISH_PUNCTUATION + SPECIAL_PUNCTUATION + MATH_PUNCTUATION
