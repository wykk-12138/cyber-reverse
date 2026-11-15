import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

pat = re.compile(r"method\(([^,]+), '([A-Za-z]+)'")
rows = []
for m in pat.finditer(text):
    target = m.group(1).strip()
    name = m.group(2)
    rows.append((target, name))

seen = []
for target, name in rows:
    if (target, name) not in seen:
        seen.append((target, name))

print(len(seen), "distinct sites")
for target, name in seen:
    print(f"{target:42} {name}")
