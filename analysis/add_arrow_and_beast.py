import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Modules\Registry.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''        // BSTN is not Shopify: it runs its own /api/beast/ prefix and checks out through Adyen.'''
addition = '''        // R91: the image names this store outright — the display string "ARROW & BEAST" and two
        // hosts, https://arrowandbeast.com/ and https://arrowbeast.myshopify.com/. It is a Shopify
        // storefront with its own domain in front, which is exactly the ShopifyFlow alias shape.
        // The replica had no such store before; the binary says it has one.
        new FlowStoreModule(new ShopifyFlow("arrowandbeast", "Arrow & Beast",
            new[] { "arrowandbeast.com", "arrowbeast.myshopify.com" })),

        // BSTN is not Shopify: it runs its own /api/beast/ prefix and checks out through Adyen.'''

if anchor not in t:
    raise SystemExit("registry anchor missing")
if "arrowandbeast" in t:
    raise SystemExit("already registered")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, addition, 1))
print("Arrow & Beast registered")
