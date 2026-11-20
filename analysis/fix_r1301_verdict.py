"""R1301 self-correction patch: 0x14094c210 is a request-configuration delegate.

The first write-up called it a response handler. `sub_1408B61E0` invokes the
delegate inside itself, immediately before `sub_1408B5EB0` sends, on the request
object it just built -- so it configures the outgoing request. And the apiKey
literal is not read on this chain at all: its four referencing functions are
sub_14094DEB0 / sub_1409F2A60 / sub_140ECF2B0 / sub_14117B6C0, none in 0x14095xxxx.

Patched by script rather than the editor because the editor refuses this file as
binary; the console cannot round-trip its Chinese. Counts are asserted so a
mis-aimed replacement aborts instead of silently editing the wrong paragraph.
"""
import io
import sys

PATH = 'replica/docs/VERDICT.md'

BEFORE = (
    "  `https://www.casio.com/{storeCode}/rest/V1/stripe/payments/get_stripe_configuration?_=<tick>`\uff0c\n"
    "  \u54cd\u5e94\u952e `apiKey`\u3002\u21d2 **\u5b83\u4e0d\u662f Unzer\uff0c\u662f Casio Magento \u7684 Stripe \u914d\u7f6e\u7aef\u70b9**\uff0c"
    "\u4e0e\u540c\u9875 `sub_14095c980` \u7684\n"
    "  `/stripe/payments/get_requires_action?orderId=` \u540c\u65cf\u3002\u590d\u523b\u4ef6\u91cc `get_stripe_configuration` \u4e0e\n"
    "  `webSdkBootstrap` \u90fd\u8fd8\u4e0d\u5b58\u5728\uff0c\u843d\u7801\u4e0b\u8f6e\u505a\u3002\n"
)

AFTER = (
    "  `https://www.casio.com/{storeCode}/rest/V1/stripe/payments/get_stripe_configuration?_=<tick>`\uff0c\n"
    "  \u4e0e\u540c\u9875 `sub_14095c980` \u7684 `/stripe/payments/get_requires_action?orderId=` \u540c\u65cf\u3002\u21d2 **\u5b83\u4e0d\u662f Unzer\uff0c\n"
    "  \u662f Casio Magento \u7684 Stripe \u914d\u7f6e\u7aef\u70b9**\u3002\u590d\u523b\u4ef6\u91cc `get_stripe_configuration` \u4e0e `webSdkBootstrap`\n"
    "  \u90fd\u8fd8\u4e0d\u5b58\u5728\uff0c\u843d\u7801\u4e0b\u8f6e\u505a\u3002\n"
    "- **\u540c\u4e00\u8f6e\u5185\u81ea\u6211\u66f4\u6b63\u4e00\u5904**\uff1a\u5148\u524d\u628a `0x14094c210` \u8bfb\u6210\u300c\u54cd\u5e94\u5904\u7406\u5668\u300d\u3002"
    "`sub_1408B61E0` \u7684\n"
    "  `(*(a3+32))(*(a3+8), v6)` \u662f\u5728 `sub_1408B5EB0` **\u53d1\u9001\u4e4b\u524d**\u8c03\u7528\u5b83\uff0c`v6` \u662f\u521a\u6784\u9020\u51fa\u6765\u7684\u8bf7\u6c42\u5bf9\u8c61 \u21d2\n"
    "  \u5b83\u662f**\u53d1\u8bf7\u6c42\u524d\u7684\u914d\u7f6e\u59d4\u6258**\uff0c\u4e0d\u662f\u54cd\u5e94\u56de\u8c03\u3002`apiKey` \u7684\u8bfb\u53d6\u65b9\u4e5f**\u4e0d\u5728**\u8fd9\u6761\u94fe\u4e0a\uff1a\n"
    "  `0x146f7544c` \u7684 4 \u4e2a\u5f15\u7528\u8005\u662f `sub_14094DEB0`\u3001`sub_1409F2A60`\u3001`sub_140ECF2B0`\u3001`sub_14117B6C0`\uff0c\n"
    "  \u65e0\u4e00\u5728 `0x14095xxxx`\u3002\n"
)

text = io.open(PATH, encoding='utf-8').read()
n = text.count(BEFORE)
print('occurrences found: %d (want 1)' % n)
if n != 1:
    sys.exit(1)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(BEFORE, AFTER))
print('patched %s' % PATH)
