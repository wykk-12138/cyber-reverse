"""R1306 roadmap patch, second attempt: the anchor moved when R1302 rewrote the bullet.

The line is split across two source lines, so the earlier single-line anchor missed. This one targets the
two-line tail exactly and asserts its count.

Byte-level, count-asserted, UTF-8.
"""
import io
import sys

PATH = 'docs/REMAINING_REPLICATION_ROADMAP.md'

BEFORE = (
    '\u3002Unzer \u4fa7\u4ecd\u4f59\n'
    "     `qword_1472c65a0+8` \u7ec8\u6001\u96c6\u5408\u4e0e `0x14094a870` \u8c13\u8bcd\u4e24\u9879\uff1b\n"
)

AFTER = (
    '\u3002**Unzer \u4fa7\u4e24\u9879 R1306 \u5df2\u7ed3\u6848**\uff1a`0x14094a870` = \u4e24\u4e2a '
    '`IndexOf(OrdinalIgnoreCase)`\uff08`unzer.com` / `heidelpay`\uff09\u2192 `IsUnzerThreeDsUrl`\uff1b\n'
    '     `qword_1472c65a0+8` **\u4e0d\u662f\u54c8\u5e0c\u8868**\uff0c\u5b83\u7684\u61d2\u521d\u59cb\u5316\u5668 `sub_14094AB00` \u5206\u914d\u4e00\u4e2a\u5341\u5143 '
    '`string[]` \u88c5\u5341\u53e5\u5931\u8d25\u63aa\u8f9e \u2192 `TerminalPhrases` / `IsTerminalFailure`\uff0c\n'
    '     \u5e76\u5df2\u5728 `RunUnzerThreeDsAsync` \u8d77\u70b9\u63a5\u5165\uff08\u9875\u9762\u8bf4\u300cdeclined\u300d\u5c31\u6b64\u7ed3\u675f\uff0c\u4e0d\u518d\u8ddf\u8df3\uff09\uff1b\n'
)

text = io.open(PATH, encoding='utf-8').read()
n = text.count(BEFORE)
print('found=%d (want 1)' % n)
if n != 1:
    sys.exit(1)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(BEFORE, AFTER))
print('patched %s' % PATH)
