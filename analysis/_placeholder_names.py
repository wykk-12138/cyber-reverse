"""R1160: which overrides are the placeholders?

tools/flow_work_audit.py reports counts only, so the twelve rows it calls placeholders are anonymous.
This mirrors its classifier (same regexes, same delegation rule from R986) and prints the names, which is
what makes them actionable: a placeholder on a store that can be reached is work, a placeholder on a
credential-blocked store is a known Unknown with a reason.
"""
import io
import os
import re

FLOWS = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

OVERRIDE = re.compile(
    r"public\s+override\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)\s*Async\s*\([^)]*\)\s*"
    r"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\s*=>[^;]*;)", re.S)
OUTCOME = re.compile(r"StepOutcome\.(?:Fail|Stop|Success)\s*\([^;]*?\)", re.S)
DELEGATION = re.compile(r"\b\w*Async\s*\(|\b\w+Core\s*\(|\bOpen\w*\s*\(")


def classify(body):
    rest = OUTCOME.sub("", body)
    if re.search(r"\bawait\b|\bHttp\b|\bc\.Session\b|\bc\.Vars\b|\bthrow\b", rest):
        return True
    return bool(DELEGATION.search(rest))


total = 0
for name in sorted(os.listdir(FLOWS)):
    if not name.endswith("Flow.cs"):
        continue
    text = io.open(os.path.join(FLOWS, name), encoding="utf-8", errors="replace").read()
    rows = []
    for step, body in OVERRIDE.findall(text):
        if not classify(body):
            rows.append((step, " ".join(body.split())[:90]))
    if rows:
        print("== %s  (%d placeholder)" % (name[:-len("Flow.cs")], len(rows)))
        for step, body in rows:
            print("     %-26s %s" % (step, body))
        total += len(rows)
print()
print("total placeholders:", total)
