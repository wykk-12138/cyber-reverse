"""R1144: finish the probe in health-checked chunks.

Two runs in a row died somewhere after roughly twenty-five sequential analysis/ida.py calls, which
looks like the transport degrading rather than any property of the patterns. So this probes in chunks
of 12, asks for health between chunks, and resumes from where it stopped instead of restarting -- a
loop that dies at a fixed distance needs a checkpoint, not more retries.
"""
import json
import re
import subprocess
import sys
import time

PY = r"python"
IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

PENDING = [
    "/view/basket/add", "/view/component/basket/minibasketAjax", "/view/resources/getUserInfo",
    "/v1/product_variants/buy_bar_data",
    "https://a.klaviyo.com/client/subscriptions/confirm",
    "https://api.nike.com/product_feed/threads/v2/",
    "https://api.omise.co", "https://api.paypal.com/v1/oauth2/token",
    "https://api.paypal.com/v2/checkout/orders", "https://api.sandbox.paypal.com",
    "https://api.pocketgames.nl/v1/public/drop-schedule",
    "https://api.pocketgames.nl/v1/public/raffle-entry",
    "https://p01.mul-pay.jp/payment/SaveCard.idPass", "https://search.scheels.com",
    "https://www.bstn.com/", "https://yzy-prod.swell.store",
]

STATE = r"D:\projects\cyber-reverse\analysis\.flow_url_pending.json"


def call(args):
    p = subprocess.run([PY, IDA] + args, capture_output=True, text=True, timeout=300)
    return p.stdout


def healthy():
    out = call(["health"])
    return '"status":"ok"' in out.replace(" ", "")


def probe(pattern):
    out = call(["str", re.escape(pattern), "--limit", "3"])
    try:
        i = out.find("{")
        d = json.JSONDecoder().raw_decode(out[i:])[0]
        return d.get("n", 0)
    except Exception:
        return -1


results = {}
done = []
for idx, lit in enumerate(PENDING):
    if idx % 12 == 0 and not healthy():
        print("transport unhealthy before chunk at", lit, "-- stopping", file=sys.stderr)
        break
    shapes = [lit] + ([lit.lstrip("/")] if lit.startswith("/") else [])
    if "://" in lit:
        shapes.append(lit.split("://", 1)[1])
    verdict = "untested"
    for sh in shapes:
        n = probe(sh)
        if n < 0:
            verdict = "untested"
            break
        if n > 0:
            verdict = "present:" + sh
            break
        verdict = "absent"
    results[lit] = verdict
    done.append(lit)
    print("%-9s %s" % (verdict[:9], lit))
    time.sleep(0.2)

json.dump({"results": results, "remaining": [l for l in PENDING if l not in done]},
          open(STATE, "w", encoding="utf-8"), indent=2)
print("probed", len(done), "remaining", len(PENDING) - len(done))
