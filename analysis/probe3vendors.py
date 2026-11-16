"""Probe Shape, Signifyd and Riskified for the header and cookie names a Vendor record would need. (R807)"""

import json
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"


def strings(pattern):
    out = subprocess.run([sys.executable, IDA, "str", pattern], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return []
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return []
    return [m["string"] for m in d.get("matches", [])]


for name in ("shape", "signifyd", "riskified"):
    rows = sorted({s for s in strings(name) if 3 < len(s) < 100})
    print("  === %s : %d ===" % (name, len(rows)))
    for s in rows[:22]:
        print("      " + s[:96])
    print()
