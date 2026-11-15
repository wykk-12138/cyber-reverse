import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("/v5/ paths", r"/v5/[A-Za-z0-9_\-/{}$:?=&%]+"),
    ("scheels hosts", r"[A-Za-z0-9\-\.]*scheels\.com[A-Za-z0-9_\-/\.{}$:?=&%]*"),
    ("/v4/ paths", r"/v4/[A-Za-z0-9_\-/{}$:?=&%]+"),
):
    hits = sorted(set(re.findall(pat, text)))
    print("=== %s (%d)" % (label, len(hits)))
    for h in hits[:24]:
        print("   ", h[:110])
    print()
