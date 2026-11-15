import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

targets = ("DetectAsync", "SolveWafAsync", "RemoteSolve", "SolveBotD")

for t in targets:
    print("=== neighbours of", t)
    shown = 0
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if t in body:
            print("   ", body[:220])
            shown += 1
            if shown >= 3:
                break
    print()

print("=== status/verb strings that say WHEN a wall is handled")
patterns = [
    r"[A-Z][a-z]+ (?:the )?(?:WAF|wall|challenge|antibot) [a-z ]{4,40}",
    r"(?:before|after) (?:the )?(?:request|response|checkout|cart)[a-z ]{0,30}",
    r"(?:on|upon) (?:403|401|429|challenge)[a-z ]{0,30}",
]
seen = set()
for pat in patterns:
    for m in re.finditer(pat, text):
        s = m.group(0).strip()
        if s.lower() in seen:
            continue
        seen.add(s.lower())
        print("   ", s[:90])
        if len(seen) > 24:
            break
