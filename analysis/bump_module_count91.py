import io, re

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica"

# R91 added one module: 61 -> 62. Four guards point at that number.
edits = [
    (base + r"\tests\Cybersole.Tests\CoreTests.cs", "Assert.Equal(61,", "Assert.Equal(62,"),
    (base + r"\docs\PARITY.md", "61 个", "62 个"),
    (base + r"\docs\VERDICT.md", "61 个", "62 个"),
    (base + r"\docs\VERDICT.md", "| 61 |", "| 62 |"),
]

for path, old, new in edits:
    t = io.open(path, encoding="utf-8").read()
    if old not in t:
        print("skip (not found):", path.rsplit("\\", 1)[-1], old)
        continue
    n = t.count(old)
    t = t.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(t)
    print("%-16s %-12s x%d" % (path.rsplit("\\", 1)[-1], old, n))

# mutation-check anchors mention the module count too
p = base + r"\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()
before = t
t = t.replace('"find": "61 个"', '"find": "62 个"')
t = t.replace('"replace": "60 个"', '"replace": "61 个"')
if t != before:
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("mutation-check anchors updated")
else:
    print("mutation-check: no module-count anchor found")
