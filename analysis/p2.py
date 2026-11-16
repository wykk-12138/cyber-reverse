import io
import json
import os

# Classifying hosts as store or vendor is a judgement, so it is written out rather than inferred from the
# name. A store host is one where the domain belongs to a retailer the replica has a module for; a vendor
# host is a payment processor, a protection service or other third party whose paths a store calls but does
# not own. Coverage means different things for the two, which is why R895's mixed 32.2% was unclear.
VENDOR = {
    "challenges.cloudflare.com",        # Turnstile
    "flex.cybersource.com",             # 3DS Flex
    "www.paypal.com",                   # 3DS
    "app.midtrans.com",                 # Snap payment
    "checkoutshopper-live.adyen.com",   # Adyen checkoutshopper
    "api.braintreegateway.com",         # Braintree client API
    "api.sibspayments.com",             # SIPS payment form
    "www.vivapayments.com",             # Viva checkout
    "payments.bigcommerce.com",         # BigCommerce payments
    "webservices.global-e.com",         # Global-e cross-border checkout
    "static-forms.klaviyo.com",         # Klaviyo forms
    "pbiouukmdvahsphokqle.supabase.co", # Supabase functions
    "inbox-api.aycd.io",                # AYCD captcha/OTP inbox
    "api.vipps.no",                     # Vipps
    "www.ibm.com",                      # suspected stray string
}

raw = io.open(r"D:/projects/cyber-reverse/analysis/.p1.txt", encoding="utf-8", errors="replace").read()
i = raw.find("{")
d, _ = json.JSONDecoder().raw_decode(raw[i:])
res = (d.get("result") or "") + (d.get("stdout") or "")

paths = {}
hosts = {}
for l in res.splitlines():
    if not l.startswith("P\t"):
        continue
    _, fam, host, p = l.split("\t")
    hosts[fam] = host
    paths.setdefault(fam, set()).add(p)

rep = []
for dp, _dirs, fs in os.walk(r"D:/projects/cyber-reverse/replica/src"):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                rep.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
rep_all = "\n".join(rep)


def covered(p, fam):
    if ('"' + p + '"') in rep_all:
        return True
    tail = p[len(fam):]
    return len(tail) > 4 and ('"' + tail + '"') in rep_all


store = {"total": 0, "have": 0}
vendor = {"total": 0, "have": 0}
store_hosts, vendor_hosts = set(), set()
for fam in sorted(paths):
    host = hosts[fam]
    is_vendor = host in VENDOR
    bucket = vendor if is_vendor else store
    (vendor_hosts if is_vendor else store_hosts).add(host)
    for p in sorted(paths[fam]):
        bucket["total"] += 1
        if covered(p, fam):
            bucket["have"] += 1

print("store hosts : %d   paths %d, covered %d (%.1f%%)"
      % (len(store_hosts), store["total"], store["have"],
         100.0 * store["have"] / max(store["total"], 1)))
print("vendor hosts: %d   paths %d, covered %d (%.1f%%)"
      % (len(vendor_hosts), vendor["total"], vendor["have"],
         100.0 * vendor["have"] / max(vendor["total"], 1)))
print("")
print("unclassified hosts: %s"
      % sorted(set(hosts.values()) - VENDOR - store_hosts) or "none")
print("")
print("store hosts:")
for h in sorted(store_hosts):
    print("  " + h)
