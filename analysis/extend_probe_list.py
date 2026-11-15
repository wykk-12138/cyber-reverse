import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ShopifyWrappingTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '"bodega.com", "cncpts.com",'
new = '"arrowandbeast.com", "arrowbeast.myshopify.com", "bodega.com", "cncpts.com",'

if old not in t:
    raise SystemExit("probe-list anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("probe list extended")
