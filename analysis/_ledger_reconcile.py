"""R1146: read the existing endpoint ledger and reconcile it with R1144's absent list.

R1143/R1144 spent two rounds re-deriving what tests/EndpointLedgerTests.cs already classifies, so this
reads that table first and reports which of the confirmed-absent literals are already accounted for and
which are genuinely unclassified. Only the second group deserves code changes.
"""
import io
import json
import re
from collections import Counter

LEDGER = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointLedgerTests.cs"
ABSENT = r"D:\projects\cyber-reverse\analysis\.flow_url_verdict2.json"

text = io.open(LEDGER, encoding="utf-8").read()
rows = re.findall(r'\[\s*"([^"]+)"\s*\]\s*=\s*"([^"]*)"', text)
print("ledger rows:", len(rows))
print("kinds:", dict(Counter(k for _, k in rows)))
print("tests:", [m.group(1) for m in re.finditer(r"public void (\w+)", text)])

ledger = {p: k for p, k in rows}
verdict = json.loads(io.open(ABSENT, encoding="utf-8").read())
absent = [r[0] if isinstance(r, list) else r for r in verdict["absent"]]

print()
print("R1144 confirmed-absent:", len(absent))
already, unclassified = [], []
for lit in absent:
    kind = ledger.get(lit)
    if kind is None:
        # also try with and without the leading slash
        alt = lit.lstrip("/") if lit.startswith("/") else "/" + lit
        kind = ledger.get(alt)
        if kind is not None:
            lit = alt + "  (matched without/with slash)"
    (already if kind else unclassified).append((lit, kind))

print("already classified in the ledger:", len(already))
for lit, kind in already:
    print("   %-8s %s" % (kind, lit))
print("NOT in the ledger:", len(unclassified))
for lit, _ in unclassified:
    print("   ?        %s" % lit)
