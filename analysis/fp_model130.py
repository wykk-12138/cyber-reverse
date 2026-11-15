import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== backing fields (Fingerprint model)")
seen = set()
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    for m in re.finditer(r"<([A-Z][A-Za-z0-9]+)>k__BackingField", body):
        seen.add(m.group(1))
for name in sorted(seen):
    print("   ", name)

print()
print("=== Fingerprint.template.json neighbourhood")
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "template.json" in body:
        print("   ", body[:200])
        break
