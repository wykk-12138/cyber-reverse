import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

needles = ["graphql", "gid://", "cartCreate", "cartLines", "SellingPlan", "inContext",
           "checkoutUrl", "storefront", "X-Shopify", "shopify"]

seen = set()
for line in lines:
    body = line.split("  ", 1)[-1]
    low = body.lower()
    if not any(n.lower() in low for n in needles):
        continue
    if body in seen:
        continue
    seen.add(body)
    print("  ", body[:150])
