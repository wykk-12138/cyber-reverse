import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("johnlewis bff", r"checkout\.johnlewis\.com/bff/[A-Za-z0-9_\-/\.{}$:?=&%]+"),
    ("scheels frontastic", r"apihub\.scheels\.com/frontastic/[A-Za-z0-9_\-/\.{}$:?=&%]+"),
    ("scheels other", r"[A-Za-z0-9_\-\.]*scheels\.com/[A-Za-z0-9_\-/\.{}$:?=&%]*"),
):
    hits = sorted(set(re.findall(pat, text)))
    print("=== %s (%d)" % (label, len(hits)))
    for h in hits[:30]:
        print("   ", h[:120])
    print()
