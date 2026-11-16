"""Find scheels in the replica and read its flow. (R808)

R807 established that Signifyd is a handled vendor in the image, with a step-up state machine and two frontastic cart
actions on apihub.scheels.com. Before implementing anything, check what the replica's scheels module looks like and
whether the step-up belongs in it.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica\src"

hits = []
for base, _d, files in os.walk(ROOT):
    if os.sep + "obj" in base or os.sep + "bin" in base:
        continue
    for f in files:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(base, f)
        t = io.open(p, encoding="utf-8", errors="replace").read()
        for i, line in enumerate(t.splitlines(), 1):
            if re.search(r"[Ss]cheels", line):
                hits.append((os.path.relpath(p, ROOT), i, line.strip()))

print("  scheels mentions: %d" % len(hits))
for path, i, line in hits[:40]:
    print("    %-46s %4d  %s" % (path, i, line[:78]))

print()
# If there is a ScheelsFlow, show its overrides.
for base, _d, files in os.walk(ROOT):
    if os.sep + "obj" in base or os.sep + "bin" in base:
        continue
    for f in files:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(base, f)
        t = io.open(p, encoding="utf-8", errors="replace").read()
        m = re.search(r"class\s+(\w*Scheels\w*)", t)
        if not m:
            continue
        print("  found %s in %s" % (m.group(1), os.path.relpath(p, ROOT)))
        start = m.start()
        nxt = t.find("\nclass ", start + 10)
        seg = t[start:nxt if nxt > start else start + 6000]
        for line in seg.splitlines():
            s = line.strip()
            if re.search(r'override\s+(async\s+)?Task<StepOutcome>|override\s+bool|const string', s):
                print("      " + s[:96])
