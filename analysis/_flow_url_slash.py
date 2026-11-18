"""R1144: re-probe the confirmed-absent literals with a slash-insensitive shape.

R1143 compared each literal exactly as written, and most of the flow sources write a leading slash
('/cart/add.js') while the image may store the segment without one ('cart/add.js'). That is the same
probe-shape mistake as testing only scheme-qualified hosts, so before any of those 27 is called
invented, each gets probed bare as well as slashed.
"""
import idautils
import ida_strlist

LITERALS = [
    "/api/cart/add", "/cart/add.js", "/api/beast", "/geoIP", "/api/payments", "/api/payments/",
    "/v1/buys", "/api/v2/shop/countries", "/account/verify", "/checkout/#payment",
    "/collections/new-releases", "/rest/V1/carts/mine", "/rest/V1/carts/mine/totals",
    "/rest/V2/carts/mine", "/api/order/submit", "/api/stock", "/api/checkout/submit",
    "/api/preorder/entry", "/path", "/api/cart/items", "/api/search", "/cart/update.js",
    "/account/recover", "/account?email=", "/buy/carts/v2/app", "/checkout/complete", "/discount/",
]

ida_strlist.build_strlist()
parts = []
for si in idautils.Strings():
    parts.append(str(si))
blob = "\n".join(parts)
print("image strings:", len(parts))

for lit in LITERALS:
    shapes = []
    bare = lit.lstrip("/")
    shapes.append(bare)
    if "?" in lit:
        shapes.append(lit.split("?")[0].lstrip("/"))
    hit = None
    for sh in shapes:
        if len(sh) >= 4 and sh in blob:
            hit = sh
            break
    print("   %-6s %s%s" % ("PRESENT" if hit else "absent", lit, ("  as %r" % hit) if hit else ""))
