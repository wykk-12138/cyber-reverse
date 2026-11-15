import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = []
for i, line in enumerate(lines, 1):
    if "61" in line:
        out.append("%d: %s" % (i, line.strip()[:140]))

io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\verdict61.txt", "w",
        encoding="utf-8", newline="").write("\n".join(out))
print("lines containing 61:", len(out))
