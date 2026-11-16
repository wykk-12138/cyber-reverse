"""Which of the image's AddToCart variants exist in the replica.

Why this exists: R906 measured async-method coverage at twenty percent and called the figure an upper bound, because
renaming is allowed and an absent name can mean a present feature under another name. This checks that claim on the
one family where it can be checked cheaply -- fifteen names that all describe the same operation, so a variant that
is absent while its plain form is present is a strong candidate for a rename rather than a gap, and a variant whose
behaviour differs is a real gap.

Not a general tool: it answers this family only, and the fifteen names are written out rather than derived, so that
the list is a record of what the image holds at the time of measuring.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"

# the image's family, with the occurrence counts recovered_async_methods.txt carries
FAMILY = [
    ("AddToCart", 32),
    ("AddToCartPreload", 11),
    ("AddToCartStoreFront", 8),
    ("AddToCartMulti", 6),
    ("AddToCartApp", 3),
    ("AddToCart2", 1),
    ("AddToCartAppDw", 1),
    ("AddToCartDummy", 1),
    ("AddToCartGraphQL", 1),
    ("AddToCartPreloadGraphQL", 1),
    ("AddToCartBox", 1),
    ("AddToCartFrontend", 1),
    ("AddToCartAstro", 1),
    ("AddToCartNext", 1),
    ("AddToCartSvelte", 1),
]

parts = []
for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                parts.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
text = "\n".join(parts)

present, absent = [], []
for name, count in FAMILY:
    hits = len(re.findall(r"\b" + re.escape(name) + r"\b", text))
    (present if hits else absent).append((name, count, hits))

print("family size: %d names, %d occurrences in the image" % (len(FAMILY), sum(c for _n, c in FAMILY)))
print("present in the replica: %d" % len(present))
print("absent from the replica: %d" % len(absent))
print("")
print("%-28s %6s %6s" % ("name", "image", "replica"))
hits_of = {n: h for n, _c, h in present + absent}
for name, count in sorted(FAMILY, key=lambda r: -r[1]):
    print("%-28s %6d %6d" % (name, count, hits_of[name]))
