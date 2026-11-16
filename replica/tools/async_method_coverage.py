"""Async method names from the image, checked against the replica's source.

Why this exists: the coverage work since R890 measured endpoint paths, which says whether a URL is named somewhere
and not whether a step exists. R905 found RunShield in the image's async-method table with no counterpart, which is
a bigger gap than a missing constant, so this measures that gap directly and over the whole table.

Not a replacement for tools/endpoint_coverage.py: paths and methods answer different questions. A path can be present
with no method behind it, and a method can exist with its URL built somewhere unexpected.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
NAMES = os.path.join(ROOT, "replica", "docs", "baseline", "recovered_async_methods.txt")

# the table is one name per line; anything else is a header the file chose to carry
names = []
for line in io.open(NAMES, encoding="utf-8", errors="replace"):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    # a line may carry a trailing count, as recovered_async_methods.txt does
    s = s.split()[0]
    if re.match(r"^[A-Za-z_]\w*$", s):
        names.append(s)
names = sorted(set(names))

# every .cs file, so a name is present anywhere rather than only in Stores
parts = []
for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                parts.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
text = "\n".join(parts)

present, absent = [], []
for n in names:
    # whole word, so Contains does not count a longer identifier as a hit
    # R911: the image's names come from state-machine types (d__NN), so they carry no Async suffix, while a C#
    # method does. A strict whole-word test therefore reports ScrapeProductAsync as missing ScrapeProduct --
    # fifty-four names were miscounted that way before this fix. Match the bare name and then the name with the
    # suffix glued on, which is one identifier and not two.
    if re.search(r"\b" + re.escape(n) + r"(?:Async)?\b", text):
        present.append(n)
    else:
        absent.append(n)

print("async names in the image: %d" % len(names))
print("async names present in the replica: %d" % len(present))
print("async names absent from the replica: %d" % len(absent))
pct = (100.0 * len(present) / len(names)) if names else 0.0
print("async names percent present: %.1f" % pct)
print("")
print("absent, first eighty:")
for n in absent[:80]:
    print("  " + n)
