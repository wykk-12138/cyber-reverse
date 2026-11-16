"""Which flows override GetHomeAsync and ignore the context URL. (R821)

R820 found PoqAppFlow doing this and noted that a flow which ignores the URL and does not meet a 403 would report a
transport error and pass the robustness test silently, leaving the ignoring invisible. This asks how many flows are in
that position, because the answer decides whether the monitor can be pointed at a URL at all for them.

The test is mechanical: find each override, take its body, and check whether it reads ctx.Url anywhere.
"""

import io
import os
import re

SRC = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

overrides = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".cs"):
        continue
    p = os.path.join(SRC, fn)
    t = io.open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"public override (?:async )?Task<StepOutcome> (GetHome\w*)\(", t):
        name = m.group(1)
        brace = t.find("{", m.end())
        if brace < 0:
            continue
        depth, i = 0, brace
        while i < len(t):
            if t[i] == "{":
                depth += 1
            elif t[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = t[brace:i + 1]
        uses_url = bool(re.search(r"\b(c|ctx)\.Url\b", body)) or "c.Url" in body
        # a flow may compose from a constant host instead
        consts = re.findall(r'"(https?://[^"]+)"', body)
        cls = None
        cm = re.search(r"public (?:sealed )?class (\w+)", t[:m.start()])
        if cm:
            cls = cm.group(1)
        overrides.append((cls or fn, name, uses_url, len(body), consts[:2]))

print("  GetHome overrides: %d" % len(overrides))
print()
print("  %-24s %-22s %-6s %s" % ("class", "method", "c.Url?", "body"))
ignoring = []
for cls, name, uses_url, n, consts in overrides:
    print("  %-24s %-22s %-6s %d" % (cls, name, "no" if not uses_url else "yes", n))
    if not uses_url:
        ignoring.append((cls, consts))

print()
print("  overrides that never read the context URL: %d" % len(ignoring))
for cls, consts in ignoring:
    print("    %-24s %s" % (cls, ", ".join(consts) if consts else "(no literal host in the body)"))
