import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for host in ("checkout.johnlewis.com", "mobile-api.scheels.com", "apihub.scheels.com"):
    pat = re.compile(re.escape(host) + r"(/[A-Za-z0-9_\-./{}$:?=&%]*)")
    paths = sorted({m.group(1) for m in pat.finditer(text)})
    print("== %s (%d)" % (host, len(paths)))
    for path in paths:
        print("   ", path[:110])
    print()
