import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for label, pat in (
    ("Stripe-* controllers", r"[A-Za-z0-9]+-Stripe[A-Za-z0-9\-]*"),
    ("Adyen* controllers", r"[A-Za-z0-9]+-Adyen[A-Za-z0-9\-]*"),
    ("CheckoutServices-*", r"Checkout[A-Za-z]*Services?-[A-Za-z]+|CheckoutServices-[A-Za-z]+"),
    ("Payment-* / -Payment", r"[A-Za-z0-9]+-Payment[A-Za-z0-9\-]*"),
):
    hits = collections.Counter(re.findall(pat, text))
    print("=== %s (%d)" % (label, len(hits)))
    for name, n in hits.most_common(14):
        print("   %-44s %d" % (name[:44], n))
    print()
