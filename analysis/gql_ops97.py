import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

ops = []
for line in lines:
    body = line.split("  ", 1)[-1]
    low = body.lower()
    if "mutation" in low or "query {" in low or "cartcreate" in low or "cartlinesadd" in low:
        ops.append(body)

print("documents found:", len(ops))
for body in ops:
    print("LEN", len(body))
    print(repr(body[:600]))
    print()
