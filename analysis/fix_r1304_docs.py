"""R1304 doc updates: the Komoju konbini `formUrl` claim is retracted and the card surface is recorded.

`0x140d98f60` does not contain a `[1..56]` suffix expression -- it builds the konbini body and takes its
URL from the state machine's context. `0x140D994D0`, the sibling card machine, does name two endpoints,
and both are now runtime constants. Leaving the old wording in place would send the next session hunting
a slice that does not exist.

Byte-level, count-asserted, UTF-8.
"""
import io
import sys

EDITS = [
    # Handoff prompt: the Komoju bullet.
    ('docs/HANDOFF_PROMPT_antigravity.md',
     '- Komoju\uff1a`0x140d98f60` `[1..56]` \u7684 `formUrl` \u540e\u7f00\u8868\u8fbe\u5f0f\uff1b',
     '- **Komoju**\uff1a`0x140d98f60` \u7684\u300c`[1..56]` `formUrl` \u540e\u7f00\u300d**\u5df2\u64a4\u56de**'
     '\uff08R1304\uff1a\u5b83\u53ea\u6784\u5efa konbini \u8bf7\u6c42\u4f53\uff0cURL \u53d6\u81ea\u72b6\u6001\u673a\u4e0a\u4e0b\u6587\uff09\uff1b'
     '\u65b0\u5df2\u89e3\u5e76\u843d\u7801\u7684\u662f\u5361\u652f\u4ed8\u9762\uff08`KomojuGateway`\uff1a`https://komoju.com/gpayments_offsite/auth` + '
     '`https://degica.as1.gpayments.net/api/v2/brw/info/result?transId=` + \u516d\u4e2a\u51bb\u7ed3 browser \u5b57\u6bb5\uff09\uff1b'
     '**\u4ecd Unknown**\uff1akonbini \u8bf7\u6c42\u4f53\u7684\u76ee\u6807 URL\uff0c\u4e0e\u5361\u51ed\u8bc1\u8bf7\u6c42\u4f53\u7684\u76ee\u6807 URL\uff1b'),
    # Roadmap item 3.
    ('docs/REMAINING_REPLICATION_ROADMAP.md',
     '  3. **Komoju \u4fbf\u5229\u5e97**\uff1a`0x140d98f60` `[1..56]` \u7684 `formUrl` \u540e\u7f00\u8868\u8fbe\u5f0f\uff1b',
     '  3. **Komoju**\uff1a`0x140d98f60` \u7684\u300c`[1..56]` `formUrl` \u540e\u7f00\u300d**R1304 \u5df2\u64a4\u56de**\u2014\u2014'
     '\u8be5\u51fd\u6570\u53ea\u6784\u5efa `\u007bauthenticity_token, payment_details:{type:konbini, email, store, given_name}\u007d`'
     '\uff08\u4e0e\u590d\u523b\u4ef6\u5df2\u6709\u7684\u4f53\u4e00\u81f4\uff09\uff0cURL \u53d6\u81ea\u72b6\u6001\u673a\u4e0a\u4e0b\u6587 `*(*(v3+16)+16)`\u3002'
     '\u540c\u65f6\u65b0\u89e3\u5e76\u843d\u7801\u4e86\u5144\u5f1f\u673a `0x140D994D0` \u7684\u5361\u9762\uff08`KomojuGateway`\uff09\u3002'
     '**\u4ecd Unknown**\uff1a`formUrl`\uff08konbini \u4e0e\u5361\u51ed\u8bc1\u4e24\u4e2a\u8bf7\u6c42\u4f53\u7684\u76ee\u6807\uff09\uff1b'),
    # External-blocked paragraph's static list.
    ('docs/PROGRESS_AND_GAP.md',
     '\u3001Komoju `formUrl` \u540e\u7f00',
     '\u3001Komoju `formUrl`\uff08\u4e24\u4e2a\u8bf7\u6c42\u4f53\u7684\u76ee\u6807\uff09'),
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
