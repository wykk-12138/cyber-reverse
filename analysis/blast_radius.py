"""Find every place that pins the module count, before deciding whether to delete five modules. (R815)

bodega, nike-gs, saintalfred, shophmvs and trophyroom have no image evidence under six search forms (R813). Deleting
them is the honest move if they are unsupported, but the count 63 and the flow-type count 33 are pinned in several
places, so the blast radius has to be known before the edit rather than discovered by red tests.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"

TARGETS = ["bodega", "nike-gs", "saintalfred", "shophmvs", "trophyroom"]

# 1) where the five appear
print("  === occurrences of the five ===")
for base, dirs, files in os.walk(ROOT):
    if any(x in base for x in (os.sep + ".git", os.sep + "obj", os.sep + "bin",
                               ".snapshots", ".mutation-backup", "target")):
        continue
    for f in files:
        if not (f.endswith(".cs") or f.endswith(".py") or f.endswith(".md") or f.endswith(".json")):
            continue
        p = os.path.join(base, f)
        try:
            t = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for mid in TARGETS:
            n = len(re.findall(r"\b" + re.escape(mid) + r"\b", t, re.I))
            if n:
                print("    %-14s %-56s %d" % (mid, os.path.relpath(p, ROOT), n))

# 2) where the counts are pinned
print()
print("  === places pinning 63 or 33 ===")
for base, dirs, files in os.walk(ROOT):
    if any(x in base for x in (os.sep + ".git", os.sep + "obj", os.sep + "bin",
                               ".snapshots", ".mutation-backup", "target")):
        continue
    for f in files:
        if not (f.endswith(".cs") or f.endswith(".py")):
            continue
        p = os.path.join(base, f)
        try:
            t = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            if re.search(r"Equal\(\s*6[0-9]\s*|Equal\(\s*3[0-9]\s*|==\s*6[0-9]\b|==\s*3[0-9]\b", line):
                if re.search(r"63|62|33|32", line):
                    print("    %-52s %4d  %s" % (os.path.relpath(p, ROOT), i, line.strip()[:70]))
