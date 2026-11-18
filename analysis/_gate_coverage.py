"""R1146: does the project's provenance ledger already cover every literal R1144 called absent?

The gate is replica/docs/ENDPOINT_PROVENANCE.md, mirrored by a 23-row dictionary in the test file and
driven by tools/endpoint-provenance.py with BASELINE = 0. This checks the whole ledger, not just the
mirror, because the mirror deliberately omits classes the tool reports differently.
"""
import io
import json
import re
from collections import Counter

LEDGER = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_PROVENANCE.md"
ABSENT = r"D:\projects\cyber-reverse\analysis\.flow_url_verdict2.json"

text = io.open(LEDGER, encoding="utf-8").read()
rows = re.findall(r"^- `(\w+)` `([^`]+)`", text, re.M)
print("ledger rows:", len(rows))
print("classes:", dict(Counter(c for c, _ in rows)))

ledger = {lit: cls for cls, lit in rows}

verdict = json.loads(io.open(ABSENT, encoding="utf-8").read())
absent = [r[0] if isinstance(r, list) else r for r in verdict["absent"]]
present = [r[0] if isinstance(r, list) else r for r in verdict["present"]]

print()
print("R1144 absent list:", len(absent))
covered, missing = [], []
for lit in absent:
    cls = ledger.get(lit)
    if cls is None:
        bare = lit.lstrip("/")
        if bare in ledger:
            cls = ledger[bare]
        else:
            for key, value in ledger.items():
                if lit.endswith(key) or key.endswith(lit):
                    cls = value
                    break
    (covered if cls else missing).append((lit, cls))

print("already classified by the gate:", len(covered))
for lit, cls in covered:
    print("   %-9s %s" % (cls, lit))
print("not in the gate:", len(missing))
for lit, _ in missing:
    print("   ?         %s" % lit)
print()
print("R1144 retractions (present after all):", len(present))
for lit in present:
    print("   PRESENT  ", lit)
