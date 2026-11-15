import io

root = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows"

# R96: the image's Shopify cart vocabulary is exactly two literals — `cart/add.js` and
# `cart/update.js`. Neither `cart/change.js` nor `cart/clear.js` occurs anywhere in it.
pairs = [
    (root + r"\ShopifyFlow.cs", "/cart/change.js", "/cart/update.js"),
    (root + r"\StoreFlow.cs", "/cart/clear.js", "/cart/update.js"),
    (root + r"\StoreFlow.cs", "/cart/change.js", "/cart/update.js"),
]

for path, old, new in pairs:
    t = io.open(path, encoding="utf-8").read()
    if old not in t:
        print("skip:", path.rsplit("\\", 1)[-1], old)
        continue
    n = t.count(old)
    io.open(path, "w", encoding="utf-8", newline="").write(t.replace(old, new))
    print("%-16s %s -> %s  x%d" % (path.rsplit("\\", 1)[-1], old, new, n))
