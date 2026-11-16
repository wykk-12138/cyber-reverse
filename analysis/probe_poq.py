"""Probe the Poq client API surface for the three steps poq-app lacks. (R805)

poq-app implements home, product, variant, add-to-cart and checkout-start, and lacks the three submit steps. The
client API is namespaced under /clients/, so the whole surface is one search wide. If checkout has steps after start,
they will be here.
"""

import json
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"


def probe(pattern):
    out = subprocess.run([sys.executable, IDA, "str", pattern], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return []
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return []
    return [m["string"] for m in d.get("matches", [])]


rows = sorted({s for s in probe("/clients/") if 8 < len(s) < 160})
print("  /clients/ strings: %d" % len(rows))
for s in rows:
    print("    " + s[:120])

print()
for pat in ("checkout/", "poq.*checkout", "checkout.*poq"):
    r = sorted({s for s in probe(pat) if 6 < len(s) < 160})
    print("  %-18s %d" % (pat, len(r)))
    for s in r[:12]:
        print("      " + s[:118])
