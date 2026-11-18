"""R1143: every URL-ish literal in the replica's flow sources, checked against the image's own strings.

Two invented endpoints were found in John Lewis alone (POST /api/delivery/address in R1133 and
POST /api/order in R1142), so the question "does any other flow call an endpoint the image has never
heard of?" deserves a sweep rather than a hunch.

Method note (AGENTS 2.7b): a hit in the image proves presence; a miss here is a *candidate*, and each
miss is re-checked with find_regex separately before it is called absent, because this script walks the
string list once and a list is not the same artefact as a search.
"""
import glob
import io
import os
import re

import idautils
import ida_strlist

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores"
LITERAL = re.compile(r'"([^"\\\n]{3,200})"')

# Collect candidate literals from the flow and payment sources.
cands = set()
files = glob.glob(os.path.join(SRC, "Flows", "*.cs")) + glob.glob(os.path.join(SRC, "Payments", "*.cs"))
for path in files:
    text = io.open(path, encoding="utf-8").read()
    for m in LITERAL.finditer(text):
        lit = m.group(1)
        if not (lit.startswith("http") or lit.startswith("/")):
            continue
        if "/" not in lit or lit.startswith("//"):
            continue
        cands.add(lit)

print("files:", len(files), "distinct literals:", len(cands))

# One blob of every string the image carries, so the per-literal test is a C-level substring search.
ida_strlist.build_strlist()
parts = []
count = 0
for si in idautils.Strings():
    count += 1
    parts.append(str(si))
blob = "\n".join(parts)
print("image strings:", count, "blob bytes:", len(blob))

present, missing = [], []
for lit in sorted(cands):
    # Interpolated segments carry '{...}'; compare only the literal part before the first brace.
    probe = lit.split("{")[0]
    if len(probe) < 3:
        continue
    (present if probe in blob else missing).append(lit)

print("present:", len(present), "missing:", len(missing))
print("---- candidates not found in the image ----")
for lit in missing:
    print("   ", lit)
