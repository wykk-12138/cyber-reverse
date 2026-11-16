"""Classify the 72 no-HTTP step overrides by what they return. (R823)

An override with no await and no HTTP call is not automatically wrong: a FindVariant parses a body fetched by an earlier
step, and a SubmitOrder that cannot proceed should say so rather than pretend. What would be wrong is one that returns
success without doing anything. This separates the three cases so the count of empty successes is a measured zero
rather than an absence of evidence.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"
CLASS = re.compile(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")
OVERRIDE = re.compile(r"public override (?:async )?Task<StepOutcome> (\w+)\(")
MEMBER = re.compile(r"^\s{4,8}(?:public|internal|protected|private)\s")
HTTPISH = re.compile(r"await|GetAsync|PostJsonAsync|PostFormAsync|SendAsync|Http\.|GetString|Fetch")
SUCCESS = re.compile(r"StepOutcome\.Success\(\)")
FAIL = re.compile(r"StepOutcome\.Fail\(")
REASON = re.compile(r'StepOutcome\.Fail\(\s*"([^"]{0,90})')


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


succ, fail, other = [], [], []
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
            body = "\n".join(lines[a:b])
            if HTTPISH.search(body.replace(m.group(0), "")):
                continue
            row = (cname, m.group(1), os.path.basename(p), b - a, body)
            if SUCCESS.search(body) and not FAIL.search(body):
                succ.append(row)
            elif FAIL.search(body) and not SUCCESS.search(body):
                fail.append(row)
            else:
                other.append(row)

print("  no-HTTP overrides: %d" % (len(succ) + len(fail) + len(other)))
print("    return only success: %d" % len(succ))
print("    return only failure: %d" % len(fail))
print("    mixed/neither:       %d" % len(other))
print()
print("  --- the ones that return only success ---")
for cname, meth, fn, n, body in succ:
    has_reason = bool(REASON.search(body))
    print("    %-22s %-32s %-20s %2d lines  reason=%s" % (cname, meth, fn, n, has_reason))
print()
print("  --- sample of the failures (they name what is missing) ---")
shown = 0
for cname, meth, fn, n, body in fail:
    m = REASON.search(body)
    if m and shown < 8:
        print("    %-20s %-30s %s" % (cname, meth, m.group(1)[:66]))
        shown += 1
