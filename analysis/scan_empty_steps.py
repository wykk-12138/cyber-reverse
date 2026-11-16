"""Find flow steps that return success without doing anything. (R823)

The coverage matrices count a step as implemented when a flow overrides it. An override that is `=> Ok()` or that
immediately returns StepOutcome.Success() counts the same as one that issues requests, so a step can satisfy the matrix
while doing nothing in particular. That is the declaration-versus-content problem R800 hit from the other side: there,
an honest failure read worse than an invented chain; here, an empty success reads better than either.

This lists overrides whose entire body is a constant success, per class, using the boundary rules that survived R822
(class by column-zero indentation, method at the next member declaration).
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"
CLASS = re.compile(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")
OVERRIDE = re.compile(r"public override (?:async )?Task<StepOutcome> (\w+)\(")
MEMBER = re.compile(r"^\s{4,8}(?:public|internal|protected|private)\s")

EMPTY_FORMS = [
    re.compile(r"^\s*=>\s*Ok\(\)\s*;\s*$"),
    re.compile(r"^\s*=>\s*StepOutcome\.Success\(\)\s*;\s*$"),
    re.compile(r"^\s*=>\s*Task\.FromResult\(StepOutcome\.Success\(\)\)\s*;\s*$"),
]


def classes(lines):
    out = []
    for i, line in enumerate(lines):
        m = CLASS.match(line)
        if m and not line.startswith((" ", "\t")):
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


def is_empty(body_lines):
    text = [l for l in body_lines if l.strip() and not l.strip().startswith(("///", "//"))]
    if not text:
        return False
    # expression-bodied
    for f in EMPTY_FORMS:
        if any(f.match(l) for l in text):
            return True
    # block with a single return
    sq = " ".join(l.strip() for l in text)
    if re.fullmatch(r"\{\s*(?:return\s+(?:Ok\(\)|StepOutcome\.Success\(\));?\s*)?\}", sq):
        return True
    return False


rows = []
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
            a, b = span(lines, i)
            body = lines[a + 1:b] if "{" not in lines[i] or lines[i].strip().startswith("public override async") else []
            if is_empty(body if body else lines[a:b]):
                rows.append((cname, m.group(1), os.path.basename(p)))

print("  overrides whose whole body is a constant success: %d" % len(rows))
for cname, meth, fn in rows:
    print("    %-24s %-34s %s" % (cname, meth, fn))

print()
from collections import Counter
c = Counter(r[0] for r in rows)
print("  per class:")
for k, v in c.most_common():
    print("    %-24s %d" % (k, v))
