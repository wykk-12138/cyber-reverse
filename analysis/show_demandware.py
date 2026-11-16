"""List every path DemandwareFlow uses, to see whether the OnePageCheckout family matches it. (R806)"""

import io
import re

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"

t = io.open(PATH, encoding="utf-8", errors="replace").read()
print("  DemandwareFlow: %d lines" % len(t.splitlines()))
print()
print("  paths and endpoints:")
seen = set()
for line in t.splitlines():
    for m in re.finditer(r'"(/[A-Za-z0-9_\-/?=&{}]*)"', line):
        p = m.group(1)
        if p not in seen and len(p) > 1:
            seen.add(p)
            print("    " + p)
print()
print("  OnePageCheckout mentioned: %s" % ("OnePageCheckout" in t))
print("  Checkout-Submit mentioned: %s" % ("Checkout-Submit" in t))
print("  dwfrm_ mentioned:          %s" % ("dwfrm_" in t))
