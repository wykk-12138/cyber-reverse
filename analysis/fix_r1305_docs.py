"""R1305 doc updates: the ToppsVariant entry stops claiming an unknown key table.

`off_1449B8EB0` is a JSON type handle, not a string table, so "the exact serialized JSON key names"
was never something that address could answer. What the image does still carry is the reflection
metadata for the type -- seven properties and four list carriers -- now modelled as `ToppsCdn`. What
remains unknown is only the serialised casing, which the reader sidesteps by matching case-insensitively.
Saying that narrowly keeps the next session from re-deriving the shape.

Byte-level, count-asserted, UTF-8.
"""
import io
import sys

EDITS = [
    ('docs/HANDOFF_PROMPT_antigravity.md',
     '- `ToppsVariant`\uff1a`off_1449B8EB0` \u7684\u7cbe\u786e\u5e8f\u5217\u5316 JSON \u952e\u540d\u3002',
     '- **Topps**\uff1a`off_1449B8EB0` \u662f **JSON \u7c7b\u578b\u53e5\u67c4\u800c\u975e\u5b57\u7b26\u4e32\u8868**\uff0c'
     '\u90a3\u4e2a\u5730\u5740\u4ece\u6765\u56de\u7b54\u4e0d\u4e86\u300c\u952e\u540d\u300d\u3002R1305 \u4ece\u955c\u50cf\u4ecd\u4fdd\u7559\u7684\u53cd\u5c04\u5143\u6570\u636e\u91cc'
     '\u8bfb\u51fa\u4e86\u7c7b\u5f62\uff08`ToppsCommerceProduct` \u4e03\u4e2a\u5c5e\u6027 + 4 \u4e2a\u5217\u8868\u627f\u8f7d\u540d\uff09\uff0c'
     '\u5df2\u843d\u6210 `ToppsCdn`\uff1b**\u4ecd Unknown** \u53ea\u5269\u5e8f\u5217\u5316\u7684\u5927\u5c0f\u5199\uff08\u8bfb\u53d6\u5668\u6309\u5927\u5c0f\u5199\u4e0d\u654f\u611f\u5339\u914d\u7ed5\u5f00\uff09\u3002'),
    ('docs/REMAINING_REPLICATION_ROADMAP.md',
     '  4. **`ToppsVariant`**\uff1a\u5728\u4e8c\u8fdb\u5236 `off_1449B8EB0` \u7684\u7cbe\u786e\u5e8f\u5217\u5316 JSON \u952e\u540d\u3002',
     '  4. **`Topps`**\uff1a**R1305 \u5df2\u7ed3\u6848\u5f62\u72b6\u9762**\u2014\u2014`off_1449B8EB0` \u662f JSON \u7c7b\u578b\u53e5\u67c4\uff0c'
     '\u4e0d\u662f\u952e\u540d\u8868\uff1b\u7c7b\u5f62\u4ece\u955c\u50cf\u7684\u53cd\u5c04\u5143\u6570\u636e\u8bfb\u51fa\uff08`ToppsCommerceProduct`\uff1a'
     '`PriceAmount` / `ProductImage` / `ProductVariant` / `SelectedOption` / `VariantImage` / '
     '`ToppsCommerceProductUrl` / `JToken`\uff0c\u52a0 `ListToppsCommerceProduct` \u7b49 4 \u4e2a\u5217\u8868\u627f\u8f7d\u540d\uff09\uff0c'
     '\u5df2\u843d\u6210 `ToppsCdn.Parse` \u5e76\u63a5\u56de `FindProductCdnAsync`\u3002'
     '**\u4ecd Unknown**\uff1a\u5e8f\u5217\u5316\u952e\u7684\u5927\u5c0f\u5199\uff08\u54cd\u5e94\u4e24\u79cd\u5199\u6cd5\u90fd\u80fd\u8bfb\uff09\u3002'),
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
before = '\u3001`ToppsVariant` JSON \u952e\u540d'
n = text.count(before)
print('%-42s found=%d' % ('docs/PROGRESS_AND_GAP.md', n))
if n == 1:
    io.open('docs/PROGRESS_AND_GAP.md', 'w', encoding='utf-8', newline='').write(
        text.replace(before, '\u3001Topps \u5e8f\u5217\u5316\u952e\u5927\u5c0f\u5199'))
else:
    ok = False

sys.exit(0 if ok else 1)
