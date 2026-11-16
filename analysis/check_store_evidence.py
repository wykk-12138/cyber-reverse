"""Check every replica module against the image's string pool. (R813)

Criterion (f) wants the original's store list taken from the binary, compared item by item with Registry.cs, with a
stated reason for every item not covered. store_catalog.py owns the replica half and keeps its logic inside main(), so
this consumes its printed rows rather than reaching into it -- a tool that works should not be refactored to be read.

The image half is a pool search per module: its id, and each of its domains as a bare host. A module with no hit at
all is listed so its reason can be written down; a module with hits is counted, not printed.
"""

import io
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
POOL = ROOT + r"\analysis\pe_strings.txt"

out = subprocess.run([sys.executable, ROOT + r"\analysis\store_catalog.py"],
                     capture_output=True, text=True)
lines = out.stdout.splitlines()

rows = []
for l in lines:
    m = re.match(r"^\s{2}(\S+)\s{2,}(.+?)\s{2,}(\S.*?)\s{2,}(\w+Flow)\s*$", l)
    if m:
        rows.append((m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)))

print("  rows parsed from store_catalog: %d" % len(rows))

pool = io.open(POOL, encoding="utf-8", errors="replace").read().lower()

def hits(needle):
    return pool.count(needle.lower())

print()
print("  modules with no pool evidence at all:")
empty = []
for mid, name, domains, flow in rows:
    needles = [mid]
    for d in re.split(r",\s*", domains):
        d = d.strip()
        if not d or d == "(none)":
            continue
        needles.append(d)
    found = sum(hits(n) for n in needles)
    if found == 0:
        empty.append((mid, name, domains, flow))
        print("    %-18s %-22s %s" % (mid, name[:22], domains[:44]))

print()
print("  modules with at least one hit: %d / %d" % (len(rows) - len(empty), len(rows)))
print("  modules with none:             %d" % len(empty))
