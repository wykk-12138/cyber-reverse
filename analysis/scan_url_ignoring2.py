"""Which GetHomeAsync overrides ignore the context URL, attributed by real class boundaries. (R822)

R821's scan credited each override to whichever class declaration last preceded it in the file, which breaks on
RetailFlows.cs where several classes share a file. The correction: find every class declaration, brace-match its body,
and only then look for overrides inside that body -- so an override can only belong to the class whose braces enclose it.

Nested classes are handled by recursing into the body rather than by reusing the outer span.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

CLASS = re.compile(r"\b(?:public|internal)\s+(?:sealed\s+|abstract\s+|static\s+|partial\s+)*class\s+(\w+)")


def body_of(text, brace_index):
    depth, i = 0, brace_index
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace_index:i + 1]
        i += 1
    return text[brace_index:]


rows = []


def walk(text, path, outer=None):
    for m in CLASS.finditer(text):
        brace = text.find("{", m.end())
        if brace < 0:
            continue
        body = body_of(text, brace)
        name = m.group(1)
        for o in re.finditer(r"public override (?:async )?Task<StepOutcome> (GetHome\w*)\(", body):
            ob = body.find("{", o.end())
            if ob < 0:
                continue
            obody = body_of(body, ob)
            rows.append({
                "file": os.path.basename(path),
                "class": name,
                "method": o.group(1),
                "uses_url": bool(re.search(r"\bc\.Url\b", obody)),
                "hosts": re.findall(r'"(https?://[^"]+)"', obody)[:2],
                "len": len(obody),
            })
        # recurse for nested classes only (their spans are inside this one)
        inner = body[1:-1]
        if CLASS.search(inner):
            walk(inner, path, outer=name)


for fn in sorted(os.listdir(SRC)):
    if fn.endswith(".cs"):
        p = os.path.join(SRC, fn)
        walk(io.open(p, encoding="utf-8", errors="replace").read(), p)

print("  GetHomeAsync overrides, attributed by class: %d" % len(rows))
print()
print("  %-26s %-22s %-6s %s" % ("class", "method", "c.Url", "file"))
ignoring = []
for r in rows:
    print("  %-26s %-22s %-6s %s" % (r["class"], r["method"], "yes" if r["uses_url"] else "NO", r["file"]))
    if not r["uses_url"]:
        ignoring.append(r)

print()
print("  overrides that never read c.Url: %d" % len(ignoring))
for r in ignoring:
    print("    %-26s %-30s %s" % (r["class"], ", ".join(r["hosts"]) if r["hosts"] else "(no literal host)",
                                  r["file"]))

# sanity: no class should carry more than a couple of GetHome overrides
from collections import Counter
c = Counter(r["class"] for r in rows)
odd = {k: v for k, v in c.items() if v > 2}
print()
print("  classes with more than two GetHome overrides (would suggest a boundary error): %s"
      % (odd if odd else "none"))
