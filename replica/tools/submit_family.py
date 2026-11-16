"""Classify the Submit family into base steps, per-provider variants, platform variants and challenges.

Why this exists: absent_checkout.py showed two hundred and forty-four checkout names absent, nearly all with a count of
one, and the three names with the highest counts -- SubmitShipping at twenty-eight, SubmitOrder at twenty-four,
SubmitPayment at twenty-two -- turned out to be present already. So the gap is not in the base steps and a count of
absent names says nothing about whether checkout works. What is needed is the split: which names are the base set,
which are provider or platform variants of it, and which are a different concern entirely.

Classification is by name, which R730 warns against. It is used to group candidates, not to claim a layer, and every
group here would need reading code before anything is built.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
NAMES = os.path.join(ROOT, "replica", "docs", "baseline", "recovered_async_methods.txt")

PROVIDERS = ("paypal", "stripe", "adyen", "unzer", "kakao", "hps", "braintree", "klarna", "amazon",
             "applepay", "googlepay", "shopify", "external", "webcomponent", "sdk", "threeDs", "threeds")
PLATFORMS = ("app", "frontend", "storefront", "astro", "next", "svelte", "commerce", "store", "mobile")
CHALLENGES = ("challenge", "captcha", "pow", "fingerprint", "clientdata", "webrtc", "browserdata",
              "botdetect", "botdeflector", "beacon", "sensor", "pat", "collect", "render", "wpt")

pairs = []
for line in io.open(NAMES, encoding="utf-8", errors="replace"):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    parts = s.split()
    if not re.match(r"^Submit\w*$", parts[0]):
        continue
    count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    pairs.append((parts[0], count))

parts_src = []
for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                parts_src.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
text = "\n".join(parts_src)


def present(name):
    return re.search(r"\b" + re.escape(name) + r"(?:Async)?\b", text) is not None


def bucket(name):
    low = name.lower()
    if any(w in low for w in CHALLENGES):
        return "challenge"
    if any(w in low for w in PROVIDERS):
        return "provider"
    if any(low.endswith(w) or low.endswith(w + "2") for w in PLATFORMS):
        return "platform"
    return "base"


groups = {}
for name, count in pairs:
    groups.setdefault(bucket(name), []).append((count, name, present(name)))

print("Submit family: %d names, %d occurrences in the image" % (len(pairs), sum(c for _n, c in pairs)))
print("")
for key in ("base", "provider", "platform", "challenge"):
    rows = sorted(groups.get(key, []), reverse=True)
    have = sum(1 for _c, _n, p in rows if p)
    occ = sum(c for c, _n, _p in rows)
    print("%-10s %3d names, %4d occurrences, %3d present in the replica" % (key, len(rows), occ, have))
    absent = [(c, n) for c, n, p in rows if not p]
    if absent:
        print("           absent: " + ", ".join("%s(%d)" % (n, c) for c, n in absent[:14]))
    print("")