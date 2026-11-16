"""Probe 'action word x bhawar' -- the variation R804 said had not been tried. (R805)

Section 2.7 says to ask how many forms a thing can take before searching. R804 searched bhawar alone and four
action words paired with casio, and named the missing combination itself. This runs it, so the ceiling claim rests on
the complete set of variations rather than the convenient ones.
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


WORDS = ["cart", "order", "checkout", "payment", "shipping", "address", "basket",
         "delivery", "submit", "place", "api"]

total = 0
for w in WORDS:
    for pat in ("%s.*bhawar" % w, "bhawar.*%s" % w):
        rows = sorted({s for s in probe(pat) if 5 < len(s) < 140})
        # the probe is a regex over the pool; drop the two host strings we already have
        rows = [s for s in rows if s.strip().rstrip("/") not in
                ("casiostore.bhawar.com", "https://casiostore.bhawar.com")]
        total += len(rows)
        if rows:
            print("  %-22s %d" % (pat, len(rows)))
            for s in rows[:6]:
                print("      " + s[:110])

print()
print("  new strings found across all %d patterns: %d" % (len(WORDS) * 2, total))
