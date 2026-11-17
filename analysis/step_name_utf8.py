"""Re-check step-name presence in the artifact using the right encoding.

R966 reported 0/179 step names present, searching UTF-16LE. The positive control found Main and Initialize present as
UTF-16 but StoreFlow, GetCsrfAsync and StepActionRunner only as UTF-8 -- so reflection metadata is stored as UTF-8 in this
image and string literals as UTF-16. The R966 check therefore searched the wrong encoding and its conclusion is void.

This reruns it against both encodings, with a control for each.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(ROOT, "src")
ART = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")
art = io.open(ART, "rb").read()

base = io.open(os.path.join(SRC, "Cybersole.Stores", "Flows", "StoreFlow.cs"),
               encoding="utf-8", errors="replace").read()
steps = sorted(set(re.findall(r"public\s+virtual\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)Async", base)))

print("  steps declared on StoreFlow: %d" % len(steps))
print()

for enc, label in (("utf-16-le", "UTF-16LE"), ("utf-8", "UTF-8")):
    hits = [s for s in steps if art.find((s + "Async").encode(enc)) >= 0]
    print("  %-10s name present: %d / %d" % (label, len(hits), len(steps)))

print()
print("  controls:")
for c in ("StoreFlow", "StepActionRunner", "NoSuchTypeAtAll", "GetCsrfAsync"):
    print("  %-20s utf16=%-5s utf8=%s" % (
        c, art.find(c.encode("utf-16-le")) >= 0, art.find(c.encode("utf-8")) >= 0))

print()
missing = [s for s in steps if art.find((s + "Async").encode("utf-8")) < 0]
print("  absent as UTF-8 (%d): %s" % (len(missing), ", ".join(missing[:12])))