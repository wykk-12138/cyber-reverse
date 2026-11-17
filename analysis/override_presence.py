"""Check whether each overridden step's own strings reach the published artifact.

R965 left this as the open question: all thirty-four hollow steps have overrides, so the gap is not in whether the steps
are implemented. The next question is whether those overrides reach the artifact, and where the missing thirty-seven
percent actually sits.

Method: for each overridden step, take a string literal that occurs inside that override and nowhere else in src, then
look for it as UTF-16LE in the published image. A hit proves the body is there. A miss does not prove absence -- R964
established that a retained method keeps only some of its strings -- so misses are reported as such rather than as
exclusions.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(ROOT, "src")
ART = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")

OVERRIDE = re.compile(r"public\s+override\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)Async")
LITERAL = re.compile(r'"([^"\\\n]{10,80})"')

texts = {}
for dp, _d, fs in os.walk(SRC):
    if os.sep + "obj" in dp or os.sep + "bin" in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            p = os.path.join(dp, fn)
            texts[p] = io.open(p, encoding="utf-8", errors="replace").read()

art = io.open(ART, "rb").read()
print("  artifact %d bytes" % len(art))

# collect each override's body and a candidate literal unique to it
rows = []
for p, t in texts.items():
    for m in OVERRIDE.finditer(t):
        step = m.group(1)
        # body: from the match to the next "public override" or 2500 chars, whichever first
        nxt = t.find("public override", m.end())
        body = t[m.end(): nxt if nxt > 0 else m.end() + 2500]

        for lit in LITERAL.findall(body):
            # unique across the whole of src?
            occurrences = sum(text.count('"' + lit + '"') for text in texts.values())
            if occurrences == 1 and len(lit) >= 12:
                rows.append((step, os.path.basename(p), lit))
                break

seen = set()
print("  %-26s %-22s %-40s %s" % ("step", "file", "unique literal", "in artifact"))
print("  " + "-" * 100)

hit = miss = 0
for step, fname, lit in rows:
    if step in seen:
        continue
    seen.add(step)
    found = art.find(lit.encode("utf-16-le")) >= 0
    if found:
        hit += 1
    else:
        miss += 1
    print("  %-26s %-22s %-40s %s" % (step, fname, lit[:38], "YES" if found else "no"))

print()
print("  overridden steps with a unique literal: %d" % len(seen))
print("  literal present in artifact: %d" % hit)
print("  literal absent (NOT proof of absence): %d" % miss)