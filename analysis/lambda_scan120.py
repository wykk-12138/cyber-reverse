import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Every lambda literal names the method it lives in and that method's ordinal.
runs = []
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if ">b__" not in body and ">g__" not in body:
        continue
    names = re.findall(r"<\s*(?:<\s*)?([A-Za-z][A-Za-z0-9_]*)\s*>\s*(?:b__|g__)\w*\|?(\d+)", body)
    if len(names) >= 4:
        runs.append((len(names), names, body))

runs.sort(key=lambda r: -r[0])
print("lambda literals with >=4 named methods:", len(runs))
print()

for count, names, body in runs[:10]:
    uniq = {}
    for name, ordinal in names:
        uniq.setdefault(int(ordinal), name)
    ordered = sorted(uniq.items())
    print("== %d lambda entries, %d methods" % (count, len(ordered)))
    print("   " + "  ".join("%d:%s" % (o, n) for o, n in ordered[:26]))
    print()
