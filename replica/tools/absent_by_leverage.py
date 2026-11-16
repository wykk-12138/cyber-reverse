"""Missing async names, ordered by how often the image uses them.

Why this exists: R906 measured coverage at twenty percent and R907 converted one family to a count, but both rounds
chose their family by what happened to be noticed. The occurrence count in recovered_async_methods.txt says how many
places in the original reference a name, so a high-count name that the replica lacks is a step used widely and
implemented nowhere -- a better target than a name that appears once.

Not a coverage tool: tools/async_method_coverage.py owns the totals. This only orders the absent names so the next
piece of work is chosen by leverage rather than by recency.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
NAMES = os.path.join(ROOT, "replica", "docs", "baseline", "recovered_async_methods.txt")

pairs = []
for line in io.open(NAMES, encoding="utf-8", errors="replace"):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    parts = s.split()
    if not re.match(r"^[A-Za-z_]\w*$", parts[0]):
        continue
    count = 1
    if len(parts) > 1 and parts[1].isdigit():
        count = int(parts[1])
    pairs.append((parts[0], count))

parts_src = []
for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                parts_src.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
text = "\n".join(parts_src)

absent = []
for name, count in pairs:
    if not re.search(r"\b" + re.escape(name) + r"\b", text):
        absent.append((count, name))

absent.sort(reverse=True)
total = sum(c for c, _n in absent)
print("absent names: %d, carrying %d image occurrences between them" % (len(absent), total))
print("")
print("%-34s %6s %8s" % ("name", "count", "cumulative"))
run = 0
for count, name in absent[:40]:
    run += count
    print("%-34s %6d %8d" % (name, count, run))
