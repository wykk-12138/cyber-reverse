import io, re, collections

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== state-machine names with Detect / Solve / AntiBot / Captcha")
names = collections.Counter()
for m in re.finditer(r"<([A-Za-z0-9_]*(?:Detect|Solve|Antibot|AntiBot|Captcha|Challenge)[A-Za-z0-9_]*)>d__(\d+)", text):
    names[m.group(1)] += 1
for name, n in names.most_common(30):
    print("   %-40s %d" % (name, n))

print()
print("=== literals that look like a step list containing Detect")
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "Detect" in body and body.count(">d__") >= 3:
        print("   ", body[:220])
        break
