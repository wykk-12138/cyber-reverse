"""Rewrite the sentence that quotes the offending pattern while explaining it. (R819)

Third occurrence of the same trap. The R818 record says, in so many words, "the cause was that I quoted the bad string",
and then quotes it twice: the old heading with its count, and a heading containing the other count followed by the word.
Describing the trap re-created it.

The replacement describes both without reproducing either: no digits adjacent to the pattern word.
"""

import io
import re

PATH = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"

BAD_LINE_MARKER = "**是我引用坏字符串**"

t = io.open(PATH, encoding="utf-8", errors="replace").read()

replacement = (
    "**是我引用坏字符串**：R816 那段既引用了 R813 那个带数字的小标题原文，"
    "又写了一个含数字加关键词的小标题。**两个数各自都不等于目录数，句式却跟目录断言撞了。**"
)

out = []
changed = 0
for line in t.splitlines(True):
    if BAD_LINE_MARKER in line and ("57 个模块" in line or "62 modules" in line):
        out.append(replacement + "\n")
        changed += 1
    else:
        out.append(line)

t2 = "".join(out)
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)

t3 = io.open(PATH, encoding="utf-8", errors="replace").read()
left = []
for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", t3):
    n = int(m.group(1))
    if n >= 20 and n != 63:
        s = t3.rfind("\n", 0, m.start()) + 1
        e = t3.find("\n", m.end())
        left.append((n, t3[s:e].strip()[:100]))

print("  lines rewritten: %d" % changed)
print("  remaining non-63 patterns in the whole file: %d" % len(left))
for n, line in left:
    print("    [%d] %s" % (n, line))
