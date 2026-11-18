"""R1143: which flow owns each absent literal, and a split between "absent" and "search errored"."""
import glob
import io
import json
import os

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores"

verdict = json.loads(io.open(r"D:\projects\cyber-reverse\analysis\.flow_url_verdict.json",
                             encoding="utf-8").read())

# The 14 whose exact search returned an error rather than a count: absent by the string-list walk only.
ERRORED = {
    "/v1/product_variants/buy_bar_data", "/view/basket/add",
    "/view/component/basket/minibasketAjax", "/view/resources/getUserInfo",
    "https://a.klaviyo.com/client/subscriptions/confirm", "https://api.nike.com/buy/carts/v2/",
    "https://api.nike.com/product_feed/threads/v2/", "https://api.omise.co",
    "https://api.paypal.com", "https://api.paypal.com/v1/oauth2/token",
    "https://api.paypal.com/v2/checkout/orders", "https://api.sandbox.paypal.com",
    "https://api.pocketgames.nl/v1/public/drop-schedule",
    "https://api.pocketgames.nl/v1/public/raffle-entry",
    "https://p01.mul-pay.jp/payment/SaveCard.idPass", "https://search.scheels.com",
    "https://www.bstn.com/", "https://yzy-prod.swell.store",
}

files = {}
for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
    files[path] = io.open(path, encoding="utf-8").read()

confirmed, errored = [], []
for lit in verdict["absent"]:
    owners = sorted({os.path.basename(p) for p, t in files.items() if lit.split("{")[0] in t})
    row = {"literal": lit, "files": owners}
    (errored if lit in ERRORED else confirmed).append(row)

confirmed.sort(key=lambda r: (r["files"][0] if r["files"] else "", r["literal"]))
print("confirmed absent (two methods):", len(confirmed))
for r in confirmed:
    print("   %-42s %s" % (r["literal"][:42], ",".join(r["files"]) or "-"))
print()
print("search errored (one method only):", len(errored))
for r in errored:
    print("   %-42s %s" % (r["literal"][:42], ",".join(r["files"]) or "-"))

io.open(r"D:\projects\cyber-reverse\analysis\.flow_url_verdict.json", "w", encoding="utf-8").write(
    json.dumps({"confirmed_absent": confirmed, "search_errored": errored}, indent=2))
print()
print("owners of confirmed absences:", sorted({f for r in confirmed for f in r["files"]}))
