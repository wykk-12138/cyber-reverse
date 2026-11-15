import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== literals containing 'structure'")
seen = set()
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "structure" in body.lower():
        key = body[:80]
        if key in seen:
            continue
        seen.add(key)
        print("   ", body[:130])

print()
print("=== literals containing 'collectplus' / 'collect plus'")
seen = set()
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    low = body.lower()
    if "collectplus" in low or "collect plus" in low:
        key = body[:80]
        if key in seen:
            continue
        seen.add(key)
        print("   ", body[:130])
