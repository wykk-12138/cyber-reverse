import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# every literal that carries a d__ ordinal run of at least three steps
cands = []
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if body.count(">d__") >= 3:
        cands.append(body)

print("literals with >=3 step names:", len(cands))
for body in cands:
    print("---- len", len(body))
    print(body)
    print()
