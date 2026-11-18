"""R1154: is the graphql stage really a PUT?

PayPalThreeDs documents "a PUT to the frozen https://www.paypal.com/graphql/ literal
(0x147097e78, send step sub_14110D670)". The verb slots are the ones the project settled long ago:
sub_1408B6310 = +24 = PUT, sub_1408B63B0 = +16 = POST, sub_1408B61E0 = +8 = GET.

This decompiles the send step and reports which slot it calls, so the verb stops being a comment and
becomes an observation.
"""
import re

import ida_hexrays

FUNC = 0x14110D670
VERB = re.compile(r"sub_1408B(6310|63B0|61E0)\(")

try:
    code = str(ida_hexrays.decompile(FUNC))
except Exception as exc:  # noqa: BLE001
    raise SystemExit("decompile failed: %s" % exc)

lines = code.split("\n")
print("lines:", len(lines))
hits = [(i, m.group(1)) for i, ln in enumerate(lines) for m in VERB.finditer(ln)]
print("verb slots called:", [(i, v) for i, v in hits])
for i, v in hits[:6]:
    name = {"6310": "PUT", "63B0": "POST", "61E0": "GET"}[v]
    print("  line %d -> %s" % (i, name))
    for j in range(max(0, i - 12), min(len(lines), i + 2)):
        s = lines[j].rstrip()
        if "147097e78" in s or "graphql" in s.lower() or "HttpMethod" in s or "Method" in s:
            print("      %5d %s" % (j, s[:140]))
