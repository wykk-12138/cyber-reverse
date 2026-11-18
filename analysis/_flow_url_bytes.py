"""R1143: settle the last sixteen candidates with a byte-level search.

The exact-search loop died with IDA partway through, so sixteen literals never got a second method.
This searches the raw bytes for each literal's UTF-16LE encoding -- an artefact independent of the
string list, which is what makes it a second method rather than a repeat of the first.
"""
import ida_bytes
import ida_ida

PENDING = [
    "/v1/product_variants/buy_bar_data",
    "/view/basket/add",
    "/view/component/basket/minibasketAjax",
    "/view/resources/getUserInfo",
    "https://a.klaviyo.com/client/subscriptions/confirm",
    "https://api.nike.com/buy/carts/v2/",
    "https://api.nike.com/product_feed/threads/v2/",
    "https://api.omise.co",
    "https://api.paypal.com",
    "https://api.paypal.com/v1/oauth2/token",
    "https://api.paypal.com/v2/checkout/orders",
    "https://api.sandbox.paypal.com",
    "https://api.pocketgames.nl/v1/public/drop-schedule",
    "https://api.pocketgames.nl/v1/public/raffle-entry",
    "https://p01.mul-pay.jp/payment/SaveCard.idPass",
    "https://search.scheels.com",
    "https://www.bstn.com/",
    "https://yzy-prod.swell.store",
]

lo = ida_ida.inf_get_min_ea()
hi = ida_ida.inf_get_max_ea()
print("range %#x..%#x" % (lo, hi))

for lit in PENDING:
    for variant, data in (("utf16", lit.encode("utf-16-le")), ("ascii", lit.encode("ascii", "ignore"))):
        ea = ida_bytes.bin_search(lo, hi, data, None, len(data), 0)
        hits = []
        while ea != ida_ida.BADADDR and len(hits) < 3:
            hits.append(ea)
            ea = ida_bytes.bin_search(ea + 1, hi, data, None, len(data), 0)
        if hits:
            print("   PRESENT %-6s %s  at %s" % (variant, lit[:60], ", ".join(hex(h) for h in hits)))
            break
    else:
        print("   ABSENT  --    %s" % lit[:70])
