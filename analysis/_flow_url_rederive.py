"""R1144: re-derive the endpoint classification through the authoritative search.

R1143 compared each literal against a string list walked with idautils.Strings(). That list turned out
to be state-dependent -- it held 324901 entries before the packed-base restore and 254117 after -- and
it does not contain literals the image demonstrably has: cart/add.js sits at 0x146fc16dc and
cart/update.js at 0x146fc175c, both of which R1143 had called invented.

So every candidate is re-put to analysis/ida.py (the plug-in's own cache) twice: as written, and with
the leading slash removed, because the sources write '/cart/add.js' while the image stores
'cart/add.js'. A hit on either shape is presence. A run that dies is untested, never absent.
"""
import json
import re
import subprocess

PY = r"python"
IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

CANDIDATES = [
    "/account/recover", "/account/verify", "/account?email=", "/api/beast", "/api/cart/add",
    "/api/cart/items", "/api/checkout/submit", "/api/order/submit", "/api/payments",
    "/api/payments/", "/api/preorder/entry", "/api/search", "/api/stock",
    "/api/v2/shop/countries", "/buy/carts/v2/app", "/cart/add.js", "/cart/update.js",
    "/checkout/#payment", "/checkout/complete", "/collections/new-releases", "/discount/",
    "/geoIP", "/path", "/rest/V1/carts/mine", "/rest/V1/carts/mine/totals",
    "/rest/V2/carts/mine", "/v1/buys", "/view/basket/add",
    "/view/component/basket/minibasketAjax", "/view/resources/getUserInfo",
    "https://a.klaviyo.com/client/subscriptions/confirm",
    "https://api.nike.com/product_feed/threads/v2/", "https://api.omise.co",
    "https://api.paypal.com/v1/oauth2/token", "https://api.paypal.com/v2/checkout/orders",
    "https://api.sandbox.paypal.com", "https://api.pocketgames.nl/v1/public/drop-schedule",
    "https://api.pocketgames.nl/v1/public/raffle-entry",
    "https://p01.mul-pay.jp/payment/SaveCard.idPass", "https://search.scheels.com",
    "https://www.bstn.com/", "https://yzy-prod.swell.store",
    "/v1/product_variants/buy_bar_data", "https://api.omise.co/v2", "/discount/x",
]


def probe(pattern):
    """Returns (hits, ok). ok=False means the tool did not answer."""
    p = subprocess.run([PY, IDA, "str", re.escape(pattern), "--limit", "3"],
                       capture_output=True, text=True, timeout=300)
    out = p.stdout
    try:
        i = out.find("{")
        d = json.JSONDecoder().raw_decode(out[i:])[0]
        return d.get("n", 0), True
    except Exception:
        return 0, False


present, absent, untested = [], [], []
for lit in CANDIDATES:
    shapes = [lit]
    bare = lit.lstrip("/")
    if bare != lit:
        shapes.append(bare)
    if "://" in lit:
        shapes.append(lit.split("://", 1)[1])

    verdict, hit_shape = None, None
    for sh in shapes:
        if len(sh) < 4:
            continue
        n, ok = probe(sh)
        if not ok:
            verdict = "untested"
            break
        if n > 0:
            verdict, hit_shape = "present", sh
            break
    if verdict == "present":
        present.append((lit, hit_shape))
    elif verdict == "untested":
        untested.append(lit)
    else:
        absent.append(lit)

print("present:", len(present))
for lit, sh in present:
    print("   PRESENT %-46s as %r" % (lit, sh))
print("absent:", len(absent))
for lit in absent:
    print("   ABSENT  %s" % lit)
print("untested (tool did not answer):", len(untested))
for lit in untested:
    print("   UNTESTED %s" % lit)

open(r"D:\projects\cyber-reverse\analysis\.flow_url_verdict2.json", "w", encoding="utf-8").write(
    json.dumps({"present": present, "absent": absent, "untested": untested}, indent=2))
