import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

seen = set()
print("=== every literal containing '/shop/v1/'")
for line in lines:
    body = line.split("  ", 1)[-1]
    if "/shop/v1/" in body:
        frag = body[body.index("/shop/v1/"):][:90]
        if frag in seen:
            continue
        seen.add(frag)
        print("  ", frag)

print()
print("=== literals mentioning popmart / pop mart")
for line in lines:
    body = line.split("  ", 1)[-1]
    low = body.lower()
    if "popmart" in low or "pop mart" in low:
        print("  ", body[:140])
