import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

PREFIXES = [
    "Cart", "CheckoutServices", "CheckoutShippingServices", "Product", "Account", "Order",
    "Payment", "Adyen", "COBilling", "COShipping", "COPlaceOrder", "Wishlist", "Address",
    "CSRF", "Search", "Login", "Profile", "OrderConfirm", "OrderShipment", "OrderRefund",
    "Store", "SourceCode", "Redirect", "RMA", "GiftCert", "Coupon", "Promotion", "Basket",
]

# A real controller literal is short and ends like a method name; the pool also holds mangled
# neighbours ("Cart-APon") and truncated copies, so require a plausible tail.
BODY = re.compile(r"\b(" + "|".join(PREFIXES) + r")-([A-Z][A-Za-z0-9]{2,40})\b")

seen = collections.Counter()
for m in BODY.finditer(text):
    name = "%s-%s" % (m.group(1), m.group(2))
    seen[name] += 1

# drop the mangled variants: names that are a strict prefix of a longer name seen at least as often
names = set(seen)
clean = set()
for name in names:
    longer = [n for n in names if n != name and n.startswith(name)]
    if longer and seen[name] <= max(seen[l] for l in longer):
        continue          # a truncated copy of a longer literal
    clean.add(name)

by_prefix = collections.defaultdict(list)
for n in clean:
    by_prefix[n.split("-")[0]].append(n)

print("clean controller literals:", len(clean))
for prefix in sorted(by_prefix, key=lambda k: -len(by_prefix[k])):
    print("\n%s (%d)" % (prefix, len(by_prefix[prefix])))
    for n in sorted(by_prefix[prefix]):
        print("   ", n)
