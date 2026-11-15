import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

patterns = {
    "shopify cart":   r"[A-Za-z0-9_\-]*/?cart/(?:add|change|update|clear)\.js",
    "shopify checkout": r"/(?:checkouts?)/[A-Za-z0-9_\-]*",
    "shopify json":   r"/products/[A-Za-z0-9_\-\.]*\.js",
    "myshopify":      r"[a-z0-9\-]+\.myshopify\.com",
    "footsites":      r"/api/[a-z0-9/_\-]*(?:checkout|cart|sites)[a-z0-9/_\-]*",
    "queueit":        r"queue-it\.net|queue\.it",
    "supreme":        r"/checkout/[a-z0-9/_\-]+",
}

for label, pat in patterns.items():
    hits = collections.Counter(re.findall(pat, text, re.IGNORECASE))
    print("=== %s (%d distinct)" % (label, len(hits)))
    for name, n in hits.most_common(12):
        print("  %-52s %d" % (name[:52], n))
    print()
