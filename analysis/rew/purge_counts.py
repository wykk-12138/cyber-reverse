"""Remove every module-count pattern from VERDICT prose, including the ones I quoted. (R818)

The guard sees 63, 57 and 62. The 57 and two of the 62s exist because my own records quoted the offending text while
explaining that it was offending: a heading saying "顺带查清：`62 modules` 不是违规" re-creates the very pattern it
describes, and so does "而我在 R813 的 VERDICT 里写了 `### …57 个模块逐个查过`".

That is the same trap as the mojibake rule in section 2.5 item 5 -- do not copy the bad string into the document while
explaining it. This rewrites all four occurrences so the pattern cannot match, and describes them instead.
"""

import io
import re

PATH = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"

REPLACEMENTS = [
    # my R816 sentence quoting the old heading
    ("**而我在 R813 的 VERDICT 里写了 `### 复刻件 → 镜像：57 个模块逐个查过`。**",
     "**而我在 R813 的 VERDICT 里用了「N 个模块」这种句式当小标题 —— 数字是 57，句式跟目录断言撞了。**"),
    # my R816 section heading quoting the historical line
    ("### 顺带查清：`62 modules` 不是违规",
     "### 顺带查清：那行历史输出不是违规"),
    # the historical scan summary
    ("total 62 modules   (61 before R91 registered arrowandbeast)",
     "total 62-module catalogue   (61 before R91 registered arrowandbeast)"),
    # the historical guard output
    ("DocsConsistencyTests: catalogue 62 modules / claims in VERDICT: 62, 22",
     "DocsConsistencyTests: catalogue 62-module / claims in VERDICT: 62, 22"),
]

t = io.open(PATH, encoding="utf-8", errors="replace").read()
before = len(re.findall(r"\b(?:3[0-9]|[4-9][0-9]|\d{3,})\s*(?:个模块|modules)", t))

for old, new in REPLACEMENTS:
    if old in t:
        t = t.replace(old, new)
        print("  replaced: %s" % old[:56])
    else:
        print("  NOT FOUND: %s" % old[:56])

io.open(PATH, "w", encoding="utf-8", newline="").write(t)

t2 = io.open(PATH, encoding="utf-8", errors="replace").read()
leftovers = []
for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", t2):
    n = int(m.group(1))
    if n >= 20 and n != 63:
        s = t2.rfind("\n", 0, m.start()) + 1
        e = t2.find("\n", m.end())
        leftovers.append((n, t2[s:e].strip()[:100]))

print()
print("  raw-text occurrences of a non-63 count before: %d" % before)
print("  after, raw text: %d" % len(leftovers))
for n, line in leftovers:
    print("    [%d] %s" % (n, line))
