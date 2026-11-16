"""Adjudicate a batch of absent names with probes, and reject probes that hit too widely. (R841)

R840 established that a probe can fail in two directions: matching nothing, or matching everything. A long hit list reads
like a conclusion while proving nothing. So each probe is judged by how many files it touches: zero means undecided,
one to five is a candidate match worth reading, and more than five means the word is too common to carry information.

Reading only -- no product code is touched.
"""

import io
import os
import sys

ROOT = r"D:\projects\cyber-reverse"
SRC = os.path.join(ROOT, "replica", "src")

# absent name -> probe words, most distinctive first
BATCH = {
    # payment channels
    "SubmitStripeOrder": ["Stripe", "stripe"],
    "ProcessOrderStripe": ["Stripe"],
    "SubmitAdyenOrder": ["Adyen", "adyen"],
    "ProcessOrderPaypalCreditCard": ["Paypal", "PayPal"],
    "SubmitUnzerOrder": ["Unzer", "unzer"],
    "ProcessOrderCommerce": ["Commerce"],
    "SubmitCheckoutPayment": ["SubmitPayment", "PaymentMethod"],
    "GetPaymentSession": ["PaymentSession"],
    # session and token
    "GetSessionToken": ["SessionToken"],
    "RequestSessionToken": ["SessionToken"],
    "GetSessionData": ["SessionData"],
    "CheckSession": ["VerifySession", "CheckSession"],
    "RestartSession": ["RestartSession"],
    "SetupProxySession": ["ProxySession"],
    "GetAtlasSessionToken": ["Atlas"],
    "GetAppCartToken": ["CartToken"],
    # checkout face
    "CreateCheckout": ["CreateCheckout"],
    "CreateCustomCheckout": ["CustomCheckout"],
    "CreateRaffleCheckout": ["RaffleCheckout", "Raffle"],
    "FinalizeCheckout": ["Finalize"],
    "GenerateCheckout": ["GenerateCheckout"],
    "LoadCheckoutPage": ["LoadCheckout", "GetCheckoutHtml", "GetCheckoutPage"],
    "ValidateCheckout": ["ValidateCheckout"],
    "VerifyCheckout": ["VerifyCheckout", "VerifyCart"],
}

sources = []
for d, _, fs in os.walk(SRC):
    for f in fs:
        if f.endswith(".cs"):
            p = os.path.join(d, f)
            sources.append((f, io.open(p, encoding="utf-8", errors="replace").read()))

def probe(word):
    hits = [(f, t.count(word)) for f, t in sources if word in t]
    return hits

rows = []
for name, words in BATCH.items():
    verdict = "undecided"
    detail = ""
    for w in words:
        hits = probe(w)
        files = len(hits)
        if files == 0:
            detail = "`%s` 0 文件" % w
            continue
        if files > 5:
            detail = "`%s` 命中 %d 文件 —— 探针无效" % (w, files)
            verdict = "probe-invalid"
            break
        site = ", ".join("%s x%d" % (f, n) for f, n in hits[:3])
        detail = "`%s` -> %s" % (w, site)
        verdict = "renamed"
        break
    rows.append((name, verdict, detail))

print("  %-30s %-14s %s" % ("absent name", "verdict", "evidence"))
for n, v, d in rows:
    print("  %-30s %-14s %s" % (n, v, d[:78]))

counts = {}
for _, v, _ in rows:
    counts[v] = counts.get(v, 0) + 1
print()
print("  totals: %s" % counts)
