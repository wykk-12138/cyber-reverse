import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "fingerprintAttempted" in body:
        print(body[:1600])
        break

print()
print("=== every browser*/threeDS* field name")
fields = set()
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    for m in re.finditer(r'"(browser[A-Za-z]+|threeDS[A-Za-z]+|challengeWindowSize|browserTZ)":', body):
        fields.add(m.group(1))
for name in sorted(fields):
    print("   ", name)
