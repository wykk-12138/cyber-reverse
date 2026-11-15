import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("rpc/ec", r"/rpc/ec/[A-Za-z0-9_\-/]+"),
    ("singlepagecheckout", r"/component/singlepagecheckout/[A-Za-z0-9_\-/]+"),
    ("gatekeeper", r"/apps/gatekeeper/[A-Za-z0-9_\-/?=&]+"),
):
    hits = sorted(set(re.findall(pat, text)))
    print("=== %s (%d)" % (label, len(hits)))
    for h in hits:
        print("   ", h)
    print()
