import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Store flows are the runs whose step names look like checkout actions, not library methods.
ACTION = re.compile(r"<(Get|Submit|Create|Add|Apply|Select|Confirm|Continue|Place|Begin|"
                    r"Start|Authorize|Validate|Check|Initiate|Generate|Handle|Web|Session|"
                    r"Guest|Delivery|Payment|Cart|Basket|Order)[A-Za-z]+>d__\d+")

hits = []
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    steps = ACTION.findall(body)
    if len(steps) >= 4:
        names = re.findall(r"<([A-Za-z]+)>d__(\d+)", body)
        hits.append((len(names), names, body))

hits.sort(key=lambda h: -h[0])
print("runs with >=4 action steps:", len(hits))
print()

for count, names, body in hits[:8]:
    print("== %d steps" % count)
    print("   " + "  ".join("%d:%s" % (int(o), n) for n, o in names))
    print()
