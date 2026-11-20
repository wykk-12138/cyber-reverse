"""R1303 doc updates: the ACS dispatcher is decoded, only the per-host handler bodies are not.

Three places described `0x1408a34f0` as an undumped branch table. It is a switch over the issuer host
name -- 28 names, 18 length cases, decoded and landed as `AcsHosts` with a cross-check that needs no
trust (the decompiler's case values and the literal lengths agree). What remains unknown is narrower and
should be stated narrowly, or the next session will re-derive the part that is already done.

Byte-level, count-asserted, UTF-8.
"""
import io
import sys

EDITS = [
    # The handoff prompt's Unknown list, second bullet.
    ('docs/HANDOFF_PROMPT_antigravity.md',
     '- Checkout.com\uff1a`0x1408a34f0` \u5c3e\u90e8\u5206\u652f\u4e2d\u6309\u53d1\u5361\u884c ACS \u4e3b\u673a\u533a\u5206\u7684\u9010\u5bb6\u8868\u5355\u5b57\u6bb5\u8868\uff1b',
     '- **Checkout.com**\uff1a`0x1408a34f0` \u7684**\u5206\u6d3e\u5c42\u5df2\u8bfb\u5b8c**\uff08R1303\uff1a28 \u4e2a\u53d1\u5361\u884c ACS \u4e3b\u673a\u540d / 18 \u4e2a\u957f\u5ea6\u5206\u652f\uff0c'
     '\u5df2\u843d\u6210 `AcsHosts`\uff09\uff0c\u5c1a\u672a\u8bfb\u7684\u662f**\u6bcf\u4e2a\u4e3b\u673a\u5904\u7406\u5668\u7684\u65b9\u6cd5\u4f53**\uff08\u9010\u5bb6\u6311\u6218\u8868\u5355\u5b57\u6bb5\u8fd8\u5728\u90a3\u91cc\u9762\uff09\uff1b'),
    # The roadmap's item 2.
    ('docs/REMAINING_REPLICATION_ROADMAP.md',
     '  2. **Checkout.com**\uff1a`0x1408a34f0` \u5c3e\u90e8\u5206\u652f\u4e2d\u6309\u53d1\u5361\u884c ACS \u4e3b\u673a\u533a\u5206\u7684\u9010\u5bb6\u8868\u5355\u5b57\u6bb5\u8868\uff1b',
     '  2. **Checkout.com**\uff1a\u5206\u6d3e\u5c42 **R1303 \u5df2\u5b8c\u6210**\u2014\u2014`0x1408a34f0` \u662f\u6309\u53d1\u5361\u884c ACS \u4e3b\u673a\u540d\u5207\u5206\u7684 switch\uff08**28 \u4e2a\u4e3b\u673a\u540d / 18 \u4e2a\u957f\u5ea6\u5206\u652f**\uff09\uff0c'
     '\u5f00\u5934\u6253 `"Starting 3DS: <host>"`\uff08\u7c7b\u76ee `3DS`\uff09\u3001\u628a\u4f20\u8f93\u6307\u7eb9\u4e34\u65f6\u6362\u6210 `chrome_131`\u3001\u5efa\u5bf9\u5e94\u5904\u7406\u5668\u3001\u518d\u628a\u539f\u6307\u7eb9\u5199\u56de\uff1b'
     '\u5df2\u843d\u6210 `AcsHosts`\uff08`Known` / `HostOf` / `IsKnown` / `ProfileFor` / `Describe`\uf09f\u4e0e `CheckoutComGateway.ResolveEswThreeDsAsync` \u63a5\u7ebf\uff09\u3002'
     '**\u4ecd Unknown**\uff1a\u6bcf\u4e2a\u4e3b\u673a\u5904\u7406\u5668\u7684\u65b9\u6cd5\u4f53\uff08\u9010\u5bb6\u6311\u6218\u8868\u5355\u5b57\u6bb5\u5728\u5176\u4e2d\uff09\uff1b'),
    # The external-blocked paragraph's static-unknown list.
    ('docs/PROGRESS_AND_GAP.md',
     'CheckoutCom \u5404\u53d1\u5361\u884c ACS \u8868\u5355\u8868',
     'CheckoutCom \u5404\u53d1\u5361\u884c ACS \u5904\u7406\u5668\u65b9\u6cd5\u4f53'),
]

ok = True
for path, before, after in EDITS:
    text = io.open(path, encoding='utf-8').read()
    n = text.count(before)
    print('%-40s found=%d' % (path, n))
    if n != 1:
        ok = False
        continue
    io.open(path, 'w', encoding='utf-8', newline='').write(text.replace(before, after))

sys.exit(0 if ok else 1)
