import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("/scapi/ paths", r"/scapi/[A-Za-z0-9_\-/{}$:?=&%.]+"),
    ("Shopper* families", r"Shopper[A-Za-z]+"),
):
    hits = collections.Counter(re.findall(pat, text))
    print("=== %s (%d distinct)" % (label, len(hits)))
    for name, n in hits.most_common(30):
        print("   %-52s %d" % (name[:52], n))
    print()
