"""R1302 doc corrections: three places still list the Unzer prepare sub-path as unknown.

It is not unknown any more, and it was never Unzer's. `0x14094C210` is the request configuration for
the Magento Stripe module's configuration fetch, whose URL `sub_14095B4E0` composes; R1302 landed it as
`StripeGateway.FetchConfigurationAsync` and deleted `UnzerGateway.PreparePaymentAsync` together with its
`unzer.prepareUrl` seam. Leaving the old wording in place would send the next session looking for a
sub-path that no longer needs finding, in a class that no longer has the step.

Byte-level, count-asserted, UTF-8 -- the console cannot round-trip these lines.
"""
import io
import sys

EDITS = [
    # 1. The handoff prompt's Unknown list, first bullet.
    ('docs/HANDOFF_PROMPT_antigravity.md',
     '- Unzer\uff1a`0x14094c210` prepare \u5b50\u8def\u5f84\u3001`qword_1472c65a0+8` \u7ec8\u6001\u96c6\u5408\u3001'
     '`0x14094a870` \u52a8\u4f5c\u5224\u5b9a\u8c13\u8bcd\uff1b',
     '- **Unzer**\uff1a`qword_1472c65a0+8` \u7ec8\u6001\u96c6\u5408\u3001`0x14094a870` \u52a8\u4f5c\u5224\u5b9a\u8c13\u8bcd\uff1b'
     '\uff08`0x14094c210` \u5df2\u5728 R1301 \u8bc1\u5b9a**\u4e0d\u5c5e\u4e8e Unzer**\u2014\u2014\u5b83\u662f Magento Stripe \u914d\u7f6e\u7aef\u70b9\u7684\u8bf7\u6c42\u914d\u7f6e\u59d4\u6258\uff0c'
     'R1302 \u5df2\u843d\u6210 `StripeGateway.FetchConfigurationAsync`\uff09\uff1b'),
    # 2. The per-gateway status table's Unzer row.
    ('docs/PROGRESS_AND_GAP.md',
     '\u5b9e\u73b0 prepare / set-payment /',
     '\u5b9e\u73b0 set-payment /'),
    # 3. The external-blocked paragraph's static-unknown list.
    ('docs/PROGRESS_AND_GAP.md',
     '\u9759\u6001\u672a\u89e3\u5b50\u5206\u652f\uff08Unzer prepare \u5b50\u8def\u5f84/\u7ec8\u6001\u96c6\u3001CheckoutCom',
     '\u9759\u6001\u672a\u89e3\u5b50\u5206\u652f\uff08Unzer \u7ec8\u6001\u96c6\u3001CheckoutCom'),
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

sys.exit(0 if ok else 1)
