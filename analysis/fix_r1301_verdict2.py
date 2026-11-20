"""R1301: second half of the self-correction -- the Inference and Unknown bullets.

Same reason as fix_r1301_verdict.py: the editor rejects this file as binary.
Counts asserted; a miss aborts.
"""
import io
import sys

PATH = 'replica/docs/VERDICT.md'

PAIRS = [
    # Inference bullet: it configures a request, and the apiKey read is off-chain.
    ("  Inference \u2014\u2014 `0x14094c210` \u662f\u300c\u53d6 Stripe \u914d\u7f6e \u2192 \u8bfb `apiKey`\u300d\u8fd9\u4e00\u6b65\u7684\u5904\u7406\u5668",
     "  Inference \u2014\u2014 `0x14094c210` \u662f\u53d1\u8bf7\u6c42\u524d\u7684\u914d\u7f6e\u59d4\u6258"),
    # Unknown bullet: name the status handlers and the flag precisely.
    ("  Unknown \u2014\u2014 \u90a3\u4e24\u4e2a\u5904\u7406\u5668\u7684\u5177\u4f53\u8bed\u4e49\uff1b`+226 = 1` \u8fd9\u4e2a\u6807\u5fd7\u4f4d\u7684\u4f5c\u7528\uff1b`webSdkBootstrap` \u5728\u4f55\u5904\u88ab\u8c03\u7528\u3002",
     "  Unknown \u2014\u2014 `200`/`400` \u4e24\u6761\u72b6\u6001\u5904\u7406\u5668\u7684\u5177\u4f53\u8bed\u4e49\uff1b`+226 = 1` \u8fd9\u4e2a\u6807\u5fd7\u4f4d\u7684\u4f5c\u7528\uff1b"
     "`apiKey` \u5230\u5e95\u7531\u54ea\u4e2a\u5f15\u7528\u8005\u8bfb\u53d6\uff1b`webSdkBootstrap` \u5728\u4f55\u5904\u88ab\u8c03\u7528\u3002"),
]

text = io.open(PATH, encoding='utf-8').read()
for before, after in PAIRS:
    n = text.count(before)
    print('found %d (want 1): %s' % (n, before[:24]))
    if n != 1:
        sys.exit(1)
    text = text.replace(before, after)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('patched %s' % PATH)
