"""R1143: re-check each candidate miss with a real search, as AGENTS 2.7b requires.

A walk over the string list proves presence but not absence, so every candidate is put to find_regex
(through analysis/ida.py, which talks to the plug-in) one literal at a time. Only a zero result there
is allowed into the absent column, and even then the count is reported as "not found by an exact
search", not as "the image never has it".
"""
import io
import json
import re
import subprocess
import sys

PY = r"python"
IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

MISSES = [
    "/account/recover", "/account/verify", "/account?email=", "/api/beast", "/api/cart/add",
    "/api/cart/items", "/api/checkout/submit", "/api/order/submit", "/api/payments",
    "/api/payments/", "/api/preorder/entry", "/api/search", "/api/stock",
    "/api/v2/shop/countries", "/buy/carts/v2/app", "/cart/add.js", "/cart/update.js",
    "/checkout/#payment", "/checkout/complete", "/collections/new-releases", "/discount/",
    "/geoIP", "/path", "/rest/V1/carts/mine", "/rest/V1/carts/mine/totals", "/rest/V2/carts/mine",
    "/v1/buys", "/v1/product_variants/buy_bar_data", "/view/basket/add",
    "/view/component/basket/minibasketAjax", "/view/resources/getUserInfo",
    "https://a.klaviyo.com/client/subscriptions/confirm",
    "https://api.nike.com/buy/carts/v2/", "https://api.nike.com/product_feed/threads/v2/",
    "https://api.omise.co", "https://api.paypal.com", "https://api.paypal.com/v1/oauth2/token",
    "https://api.paypal.com/v2/checkout/orders", "https://api.sandbox.paypal.com",
    "https://api.pocketgames.nl/v1/public/drop-schedule",
    "https://api.pocketgames.nl/v1/public/raffle-entry",
    "https://p01.mul-pay.jp/payment/SaveCard.idPass", "https://search.scheels.com",
    "https://www.bstn.com/", "https://yzy-prod.swell.store",
]

found, absent = [], []
for lit in MISSES:
    pat = re.escape(lit)
    p = subprocess.run([PY, IDA, "str", pat, "--limit", "3"], capture_output=True, text=True, timeout=300)
    out = p.stdout
    try:
        idx = out.find("{")
        obj = json.JSONDecoder().raw_decode(out[idx:])[0]
        n = obj.get("n", 0)
    except Exception:
        n = -1
    (found if n and n > 0 else absent).append((lit, n))

print("found by exact search:", len(found))
for lit, n in found:
    print("   PRESENT", n, lit)
print("absent by exact search:", len(absent))
for lit, n in absent:
    print("   ABSENT ", n, lit)

io.open(r"D:\projects\cyber-reverse\analysis\.flow_url_verdict.json", "w", encoding="utf-8").write(
    json.dumps({"found": [l for l, _ in found], "absent": [l for l, _ in absent]}, indent=2))
