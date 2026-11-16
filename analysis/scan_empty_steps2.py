"""Widen the empty-step search until it finds something, so a zero means something. (R823)

The first pass looked only for bodies that are exactly `=> Ok()` or `{ return Ok(); }` and found none. A zero from a
detector that may match nothing is not evidence, so this widens the net: every override with no await and no HTTP call
is listed with its body, which shows both what the narrow pass was missing and whether empty successes exist in a form
it did not recognise.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"
CLASS = re.compile(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")
OVERRIDE = re.compile(r"public override (?:async )?Task<StepOutcome> (\w+)\(")
MEMBER = re.compile(r"^\s{4,8}(?:public|internal|protected|private)\s")
HTTPISH = re.compile(r"await|GetAsync|PostJsonAsync|PostFormAsync|SendAsync|Http\.|GetString|Fetch")


def classes(lines):
    out = []
    for i, l in enumerate(lines):
        m = CLASS.match(l)
        if m and not l.startswith((" ", "\t")):
            out.append((i, m.group(1)))
    return out


def span(lines, start):
    for j in range(start + 1, len(lines)):
        if MEMBER.match(lines[j]):
            k = j
            while k > start + 1 and lines[k - 1].strip().startswith(("///", "[", "//")):
                k -= 1
            return start, k
    return start, len(lines)


total = 0
no_http = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".cs"):
        continue
    p = os.path.join(SRC, fn)
    lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
    cs = classes(lines)
    for idx, (ci, cname) in enumerate(cs):
        cend = cs[idx + 1][0] if idx + 1 < len(cs) else len(lines)
        for i in range(ci, cend):
            m = OVERRIDE.search(lines[i])
            if not m:
                continue
            total += 1
            a, b = span(lines, i)
            body = "\n".join(lines[a:b])
            if not HTTPISH.search(body.replace(m.group(0), "")):
                no_http.append((cname, m.group(1), os.path.basename(p), b - a, lines[i].strip()[:76]))

print("  StepOutcome overrides seen by the widened pass: %d" % total)
print("  with no await and no HTTP call: %d" % len(no_http))
print()
for cname, meth, fn, n, sig in no_http:
    print("    %-22s %-30s %-18s %2d lines" % (cname, meth, fn, n))
    print("        %s" % sig)
