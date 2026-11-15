import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("api/auth", r"/api/auth/[A-Za-z0-9_\-/\.{}$:?=&%]*"),
    ("on.com", r"[A-Za-z0-9_\-\.]*on\.com/[A-Za-z0-9_\-/\.{}$:?=&%]*"),
    ("account/login", r"/account/login[A-Za-z0-9_\-/\.{}$:?=&%]*"),
):
    hits = sorted(set(re.findall(pat, text)))
    print("=== %s (%d)" % (label, len(hits)))
    for h in hits[:28]:
        print("   ", h[:120])
    print()
