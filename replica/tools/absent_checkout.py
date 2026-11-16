"""Missing async names that belong to the checkout priority, ordered by occurrence.

Why this exists: absent_by_leverage.py ranks everything together, so the top of its list is HTTP and serialisation
plumbing — WriteToAsync, LoadAsync, WriteStartNamespaceDeclarationAsync. Those matter to the request layer, but the
ordering the user gave puts checkout flows first, so a tool that answers "what does checkout lack" has to filter.

The classification below is by name, which R730 warns against as a substitute for reading code. It is used here only
to group candidates for a human to pick from, never to claim that a name belongs to a layer; a name that lands in the
wrong bucket costs a look, not a wrong conclusion.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
NAMES = os.path.join(ROOT, "replica", "docs", "baseline", "recovered_async_methods.txt")

# words that suggest a checkout, cart, product, account or order concern rather than transport or UI
CHECKOUT = (
    "cart", "basket", "checkout", "order", "product", "sku", "variant", "size", "stock",
    "inventory", "discount", "coupon", "promo", "shipping", "delivery", "address", "payment",
    "card", "paypal", "klarna", "applepay", "googlepay", "amazon", "account", "login", "signin",
    "register", "raffle", "draw", "reserve", "reservation", "exhibit", "store", "pickup",
    "queue", "drop", "release", "restock", "monitor", "watch", "buy", "purchase",
)

pairs = []
for line in io.open(NAMES, encoding="utf-8", errors="replace"):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    parts = s.split()
    if not re.match(r"^[A-Za-z_]\w*$", parts[0]):
        continue
    count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    pairs.append((parts[0], count))

parts_src = []
for dp, _dirs, fs in os.walk(os.path.join(ROOT, "replica", "src")):
    if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            try:
                parts_src.append(io.open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read())
            except OSError:
                pass
text = "\n".join(parts_src)


def present(name):
    return re.search(r"\b" + re.escape(name) + r"(?:Async)?\b", text) is not None


relevant = [(c, n) for n, c in pairs if not present(n) and any(w in n.lower() for w in CHECKOUT)]
relevant.sort(reverse=True)

print("absent checkout-related names: %d" % len(relevant))
print("%-34s %6s" % ("name", "count"))
for count, name in relevant[:40]:
    print("%-34s %6d" % (name, count))