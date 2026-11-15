import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== literals containing 'Kasada' (first 20 distinct)")
seen = []
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "Kasada" in body and body not in seen:
        seen.append(body)
        print("   ", body[:160])
        if len(seen) >= 20:
            break

print()
print("=== names with Kasada / Kpsdk inside a state-machine or lambda")
names = set()
for m in re.finditer(r"<([A-Za-z0-9_]*(?:Kasada|Kpsdk|KPSDK)[A-Za-z0-9_]*)>(?:d__|b__|g__)", text):
    names.add(m.group(1))
for n in sorted(names):
    print("   ", n)

print()
print("=== x-kpsdk headers")
for m in sorted(set(re.findall(r"x-kpsdk-[a-z]+", text))):
    print("   ", m)
