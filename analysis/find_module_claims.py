import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
text = io.open(p, encoding="utf-8").read()

out = []
for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", text):
    line = text[:m.start()].count("\n") + 1
    s = max(0, m.start() - 50)
    e = min(len(text), m.end() + 30)
    out.append("%d  %-14s  ...%s..." % (line, m.group(0), text[s:e].replace("\n", " ")))

io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\moduleclaims.txt", "w",
        encoding="utf-8", newline="").write("\n".join(out))
print("matches:", len(out))
