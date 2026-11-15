import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# Demandware controller literals have the shape Prefix-Name, and the prefixes are a known set.
PREFIXES = [
    "Cart", "CheckoutServices", "CheckoutShippingServices", "Product", "Account", "Order",
    "Payment", "Adyen", "COBilling", "COShipping", "COPlaceOrder", "Wishlist", "Address",
    "CSRF", "Search", "Login", "Profile", "OrderConfirm", "OrderShipment", "OrderRefund",
    "Store", "SourceCode", "Redirect", "RMA", "GiftCert", "Coupon", "Promotion", "Basket",
]
pat = re.compile(r"\b(" + "|".join(PREFIXES) + r")-([A-Z][A-Za-z0-9]+)")

hits = collections.Counter()
for m in pat.finditer(text):
    hits["%s-%s" % (m.group(1), m.group(2))] += 1

print("distinct controller-shaped literals:", len(hits))
by_prefix = collections.defaultdict(list)
for name in hits:
    by_prefix[name.split("-")[0]].append(name)

for prefix in sorted(by_prefix, key=lambda k: -len(by_prefix[k])):
    names = sorted(by_prefix[prefix])
    print("\n%s  (%d)" % (prefix, len(names)))
    for n in names:
        print("   ", n)
