"""R1306 doc updates: both Unzer Unknowns are closed, so say so instead of listing them.

The handoff prompt, the roadmap and the progress doc all still carry "Unzer: qword_1472c65a0+8 terminal
set, 0x14094a870 predicate" as open. The predicate is eleven lines and the "hash table" is a
ten-element string[] of failure phrases with a named initialiser -- both are now runtime code with
tests, so the next session should not spend a round re-deriving them.

Byte-level, count-asserted, UTF-8.
"""
import io
import sys

EDITS = [
    # The handoff prompt's Unzer bullet (already rewritten once by R1302; replace the whole bullet).
    ('docs/HANDOFF_PROMPT_antigravity.md',
     '- **Unzer**\uff1a`qword_1472c65a0+8` \u7ec8\u6001\u96c6\u5408\u3001`0x14094a870` \u52a8\u4f5c\u5224\u5b9a\u8c13\u8bcd\uff1b',
     '- **Unzer**\uff1a\u4e24\u9879\u5747 **R1306 \u5df2\u7ed3\u6848**\u2014\u2014`0x14094a870` \u662f\u4e24\u4e2a '
     '`IndexOf(..., OrdinalIgnoreCase)`\uff08`unzer.com` / `heidelpay`\uff09\uff0c\u5df2\u843d\u6210 `IsUnzerThreeDsUrl`\uff1b'
     '`qword_1472c65a0+8` **\u4e0d\u662f\u54c8\u5e0c\u8868**\uff0c\u5b83\u7684\u61d2\u521d\u59cb\u5316\u5668 `sub_14094AB00` \u5206\u914d\u4e00\u4e2a\u5341\u5143 '
     '`string[]` \u88c5\u5341\u53e5\u300c\u652f\u4ed8\u5931\u8d25\u300d\uff0c\u5df2\u843d\u6210 `TerminalPhrases` / `IsTerminalFailure`\uff1b'),
    ('docs/REMAINING_REPLICATION_ROADMAP.md',
     '     **Unzer** \u4fa7\u4ecd\u4f59 `qword_1472c65a0+8` \u7ec8\u6001\u96c6\u5408\u4e0e `0x14094a870` \u52a8\u4f5c\u5224\u5b9a\u8c13\u8bcd\u4e24\u9879\uff1b',
     '     **Unzer \u4fa7\u4e24\u9879 R1306 \u5df2\u7ed3\u6848**\uff1a`0x14094a870` = \u4e24\u4e2a `IndexOf(OrdinalIgnoreCase)`'
     '\uff08`unzer.com` / `heidelpay`\uff09\u2192 `IsUnzerThreeDsUrl`\uff1b`qword_1472c65a0+8` = \u61d2\u521d\u59cb\u5316\u7684\u5341\u5143 '
     '`string[]`\uff08`sub_14094AB00`\uff0c\u5341\u53e5\u5931\u8d25\u63aa\u8f9e\uff09\u2192 `TerminalPhrases` / `IsTerminalFailure`\uff0c'
     '\u5e76\u5df2\u5728 `RunUnzerThreeDsAsync` \u8d77\u70b9\u63a5\u5165\u3002'),
]

ok = True
for path, before, after in EDITS:
    text = io.open(path, encoding='utf-8').read()
    n = text.count(before)
    print('%-42s found=%d' % (path, n))
    if n != 1:
        ok = False
        continue
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace(before, after))

text = io.open('docs/PROGRESS_AND_GAP.md', encoding='utf-8').read()
for before, after in [
    ('\u9759\u6001\u672a\u89e3\u5b50\u5206\u652f\uff08Unzer \u7ec8\u6001\u96c6\u3001', '\u9759\u6001\u672a\u89e3\u5b50\u5206\u652f\uff08'),
]:
    n = text.count(before)
    print('%-42s found=%d' % ('docs/PROGRESS_AND_GAP.md', n))
    if n == 1:
        text = text.replace(before, after)
    else:
        ok = False
io.open('docs/PROGRESS_AND_GAP.md', 'w', encoding='utf-8', newline='').write(text)

sys.exit(0 if ok else 1)
