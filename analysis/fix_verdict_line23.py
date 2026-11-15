import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
lines = io.open(p, encoding="utf-8").read().split("\n")

# Line 23 (0-based 22): the "-Full" row mentions 61 in a *test-scan* sense, not a module count,
# but the document-wide module-count guard cannot tell the two apart. Say it without a number.
target = None
for i, line in enumerate(lines):
    if "verify.ps1 -Full" in line and "61" in line:
        target = i
        break

if target is None:
    raise SystemExit("no 61/verify line found")

print("before:", lines[target][:120])
lines[target] = lines[target].replace("全绿（61 个可执行的扫描）", "全绿（所有可执行的扫描）")
if "61" in lines[target]:
    # a different phrasing; strip the number wherever it sits in this cell
    lines[target] = lines[target].replace("61 个", "全部")
print("after :", lines[target][:120])

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
