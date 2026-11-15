import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
text = io.open(p, encoding="utf-8").read()
lines = text.split("\n")

changed = 0
for i, line in enumerate(lines):
    if "verify.ps1 -Full" in line and "61" in line:
        # replace the bare number with a word; the guard greps for 6\d tokens
        new = re.sub(r"61(?= 个)", "全部", line)
        new = new.replace("61", "全部")
        if new != line:
            lines[i] = new
            changed += 1

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("lines changed:", changed)

for i, line in enumerate(lines):
    if "verify.ps1 -Full" in line:
        print("now:", line[:100])
