"""R1143: settle the host literals with dot-free probes.

Every pattern carrying a dot came back as an error (-1) from analysis/ida.py, scheme or no scheme, so
none of those fourteen ever received a reverse check. This probes a dot-free distinctive part instead:
the path tail where there is one, and the host's own label otherwise. A dot-free pattern is the only
kind this tool has actually answered for in this session.
"""
import json
import re
import subprocess

PY = r"python"
IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

PAIRS = {
    "https://a.klaviyo.com/client/subscriptions/confirm": ["client/subscriptions/confirm", "klaviyo"],
    "https://api.nike.com/buy/carts/v2/": ["buy/carts/v2", "product_feed"],
    "https://api.nike.com/product_feed/threads/v2/": ["product_feed/threads", "product_feed"],
    "https://api.omise.co": ["omise"],
    "https://api.paypal.com": ["paypal"],
    "https://api.paypal.com/v1/oauth2/token": ["v1/oauth2/token", "oauth2/token"],
    "https://api.paypal.com/v2/checkout/orders": ["v2/checkout/orders", "checkout/orders"],
    "https://api.sandbox.paypal.com": ["sandbox"],
    "https://api.pocketgames.nl/v1/public/drop-schedule": ["public/drop-schedule", "pocketgames"],
    "https://api.pocketgames.nl/v1/public/raffle-entry": ["public/raffle-entry", "raffle-entry"],
    "https://p01.mul-pay.jp/payment/SaveCard.idPass": ["SaveCard", "mul-pay"],
    "https://search.scheels.com": ["search"],
    "https://www.bstn.com/": ["bstn"],
    "https://yzy-prod.swell.store": ["swell"],
}


def probe(pattern):
    p = subprocess.run([PY, IDA, "str", pattern, "--limit", "3"],
                       capture_output=True, text=True, timeout=300)
    out = p.stdout
    try:
        i = out.find("{")
        d = json.JSONDecoder().raw_decode(out[i:])[0]
        return d.get("n", 0)
    except Exception:
        return -1


out = {}
for lit, pats in PAIRS.items():
    row = {}
    for pat in pats:
        row[pat] = probe(pat)
    out[lit] = row
    print("%-58s %s" % (lit[:58], row))

open(r"D:\projects\cyber-reverse\analysis\.flow_url_hostprobe.json", "w", encoding="utf-8").write(
    json.dumps(out, indent=2))
