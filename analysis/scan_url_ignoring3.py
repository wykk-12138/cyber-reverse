"""Attribute GetHomeAsync overrides by indentation boundaries instead of brace matching. (R822)

Two brace-matching attempts failed on RetailFlows.cs, which holds seven classes in one file: counting braces naively
lets a string or comment containing an opening brace run one class body past its end, so later classes get credited to
an earlier one. The project's own tools (bind_scope.py, member_owner_map.py) use the same rule, so this is not a defect
I introduced -- but for this question there is a method that does not care about braces at all.

Every class declaration in these files starts in column zero. A class body therefore ends at the last line before the
next column-zero `class` (or the end of the file). That is a weaker assumption than brace counting and it is not
disturbed by braces inside strings.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

starts = []  # (file, class name, first line index)
files = {}
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".cs"):
        continue
    p = os.path.join(SRC, fn)
    lines = io.open(p, encoding="utf-8", errors="replace").read().splitlines()
    files[p] = lines
    for i, line in enumerate(lines):
        m = re.match(r"(?:public|internal)?\s*(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)", line)
        if m and not line.startswith((" ", "\t")):
            starts.append((p, m.group(1), i))

by_file = {}
for p, name, i in starts:
    by_file.setdefault(p, []).append((i, name))

rows = []
for p, entries in by_file.items():
    entries.sort()
    lines = files[p]
    for idx, (i, name) in enumerate(entries):
        end = entries[idx + 1][0] if idx + 1 < len(entries) else len(lines)
        region = "\n".join(lines[i:end])
        for o in re.finditer(r"public override (?:async )?Task<StepOutcome> (GetHome\w*)\(", region):
            # take the following 40 lines as the method body approximation
            tail = region[o.end():]
            chunk = "\n".join(tail.splitlines()[:40])
            rows.append({
                "class": name,
                "method": o.group(1),
                "file": os.path.basename(p),
                "uses_url": "c.Url" in chunk,
                "hosts": re.findall(r'"(https?://[^"]+)"', chunk)[:2],
            })

print("  files with class boundaries by indentation: %d" % len(by_file))
print("  GetHomeAsync overrides found: %d" % len(rows))
print()
from collections import Counter
c = Counter(r["class"] for r in rows)
dup = {k: v for k, v in c.items() if v > 1}
print("  classes with more than one override: %s" % (dup if dup else "none"))
print()
ign = [r for r in rows if not r["uses_url"]]
print("  overrides not reading c.Url: %d" % len(ign))
for r in ign:
    print("    %-24s %-28s %s" % (r["class"], ", ".join(r["hosts"]) if r["hosts"] else "(no literal host)", r["file"]))
