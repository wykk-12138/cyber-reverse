"""Attribute GetHomeAsync by member boundaries: class by indentation, method by the next member declaration. (R822)

Both earlier attempts approximated a method body and both were wrong in opposite directions. Brace matching ran a class
past its end on RetailFlows.cs, where a brace inside a string defeats the count. A forty-line window then ran a method
past its end, so PoqAppFlow.GetHomeAsync looked like it read c.Url because the next method down does.

The boundary that works without a parser is the next member declaration: inside a class, a line that starts with an
access modifier and a signature begins a new member, and the previous method ends before it. This is the same
assumption the file already makes by convention, and it is not disturbed by braces or by method length.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

CLASS_AT_COLUMN_ZERO = re.compile(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")
MEMBER = re.compile(r"^\s{4,8}(?:public|internal|protected|private)\s")


def classes(lines):
    out = []
    for i, line in enumerate(lines):
        m = CLASS_AT_COLUMN_ZERO.match(line)
        if m and not line.startswith((" ", "\t")):
            out.append((i, m.group(1)))
    return out


def method_span(lines, start_line):
    """From the signature line, run to the line before the next member declaration."""
    for j in range(start_line + 1, len(lines)):
        if MEMBER.match(lines[j]):
            # walk back over a doc comment attached to that next member
            k = j
            while k > start_line + 1 and lines[k - 1].strip().startswith(("///", "[", "//")):
                k -= 1
            return start_line, k
    return start_line, len(lines)


rows = []
files = {}
for fn in sorted(os.listdir(SRC)):
    if fn.endswith(".cs"):
        p = os.path.join(SRC, fn)
        files[p] = io.open(p, encoding="utf-8", errors="replace").read().splitlines()

for p, lines in files.items():
    cs = classes(lines)
    for idx, (ci, cname) in enumerate(cs):
        cend = cs[idx + 1][0] if idx + 1 < len(cs) else len(lines)
        for i in range(ci, cend):
            m = re.search(r"public override (?:async )?Task<StepOutcome> (GetHome\w*)\(", lines[i])
            if not m:
                continue
            a, b = method_span(lines, i)
            body = "\n".join(lines[a:b])
            rows.append({
                "class": cname,
                "method": m.group(1),
                "file": os.path.basename(p),
                "uses_url": "c.Url" in body,
                "hosts": re.findall(r'"(https?://[^"]+)"', body)[:2],
                "lines": b - a,
            })

from collections import Counter
c = Counter(r["class"] for r in rows)
dup = {k: v for k, v in c.items() if v > 1}
print("  overrides found: %d" % len(rows))
print("  classes with more than one: %s" % (dup if dup else "none"))
ign = [r for r in rows if not r["uses_url"]]
print("  not reading c.Url: %d" % len(ign))
for r in ign:
    print("    %-24s %-28s %-18s %d lines" % (
        r["class"], ", ".join(r["hosts"]) if r["hosts"] else "(no literal host)", r["file"], r["lines"]))
print()
print("  spot checks:")
for r in rows:
    if r["class"] in ("PoqAppFlow", "NikeFlow", "YeezySupplyFlow", "SuperswipeFlow", "CasioFlow"):
        print("    %-24s uses c.Url=%-5s %d lines %s" % (r["class"], r["uses_url"], r["lines"], r["file"]))
