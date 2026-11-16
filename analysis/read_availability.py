"""Read every ScrapeVariantAvailabilityAsync and check it actually reaches a verdict. (R825)

The earlier scan found nineteen implementations that make no HTTP call and return only success. Two were read and both
did real work -- read Session.Vars["raw"], decide sold-out, write Session.Vars["available"]. That is two of nineteen, and
"two are fine" is not "all are fine": an implementation that returns success without writing the verdict would make the
monitor report whatever the previous state was, which is the silent-wrong-value shape this session keeps finding.

So this one prints each body for reading rather than scoring it. Reading only: memory is 1.29 GB and no build is needed.
"""

import io
import os
import re

FLOWS = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"
CLASS = re.compile(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")
TARGET = re.compile(r"public override (?:async )?Task<StepOutcome> ScrapeVariantAvailabilityAsync\(")
MEMBER = re.compile(r"^\s{4,8}(?:public|internal|protected|private)\s")


def classes(lines):
    return [(i, m.group(1)) for i, l in enumerate(lines)
            if (m := CLASS.match(l)) and not l.startswith((" ", "\t"))]


def span(lines, start):
    for j in range(start + 1, len(lines)):
        if MEMBER.match(lines[j]):
            k = j
            while k > start + 1 and lines[k - 1].strip().startswith(("///", "[", "//")):
                k -= 1
            return start, k
    return start, len(lines)


found = []
for fn in sorted(os.listdir(FLOWS)):
    if not fn.endswith(".cs"):
        continue
    p = os.path.join(FLOWS, fn)
    lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
    cs = classes(lines)
    for idx, (ci, cname) in enumerate(cs):
        cend = cs[idx + 1][0] if idx + 1 < len(cs) else len(lines)
        for i in range(ci, cend):
            if not TARGET.search(lines[i]):
                continue
            a, b = span(lines, i)
            body = lines[a:b]
            writes = [l.strip() for l in body if 'Vars["available"]' in l or 'Session.Vars["soldOut"]' in l
                      or "Available" in l]
            found.append((cname, fn, b - a, body, writes))

print("  ScrapeVariantAvailabilityAsync implementations: %d\n" % len(found))
silent = []
for cname, fn, n, body, writes in found:
    mark = "WRITES" if writes else "*** NO VERDICT WRITTEN ***"
    print("  --- %s (%s) %d lines : %s" % (cname, fn, n, mark))
    for l in body[1:]:
        s = l.strip()
        if s and not s.startswith("//"):
            print("      " + s[:100])
    if not writes:
        silent.append(cname)
    print()

print("  implementations that never write a verdict: %d %s" % (len(silent), silent))
