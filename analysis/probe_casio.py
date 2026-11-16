"""Probe the Casio storefront's surface for the two missing steps. (R804)

Casio is blocked on shipping and payment because `_adyenOrderId` turned out to be a field name rather than an endpoint.
Before concluding that, look at the whole host's string family rather than the two words already known.
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


for pat in ("bhawar", "casio.*(cart|order|checkout|payment|shipping|address)",
            "(cart|order|checkout|payment|shipping|address).*casio"):
    rows = sorted({s for s in probe(pat) if 5 < len(s) < 120})
    print("  --- %s : %d ---" % (pat, len(rows)))
    for s in rows[:24]:
        print("      " + s[:100])
    print()
