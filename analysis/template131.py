import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== literals with ColorDepth as JSON-ish")
seen = 0
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "ColorDepth" in body and ("{" in body or '"' in body):
        print("   ", body[:300])
        seen += 1
        if seen >= 8:
            break

print()
print("=== literals with ScreenWidth")
seen = 0
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "ScreenWidth" in body:
        print("   ", body[:300])
        seen += 1
        if seen >= 8:
            break

print()
print("=== template.json mentions")
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "template.json" in body:
        print("   ", body[:400])
