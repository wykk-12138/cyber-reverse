import io

root = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows"

# R96: the image's Shopify cart vocabulary is `cart/add.js` + `cart/update.js`.
# `cart/change.js` and `cart/clear.js` do not exist in it.
edits = [
    (root + r"\ShopifyFlow.cs", '"cart/change.js"', '"cart/update.js"'),
    (root + r"\StoreFlow.cs", '"cart/change.js"', '"cart/update.js"'),
]

for path, old, new in edits:
    t = io.open(path, encoding="utf-8").read()
    if old not in t:
        print("skip (no", old, "in", path.rsplit("\\", 1)[-1], ")")
        continue
    n = t.count(old)
    io.open(path, "w", encoding="utf-8", newline="").write(t.replace(old, new))
    print("%-16s %s -> %s  x%d" % (path.rsplit("\\", 1)[-1], old, new, n))

# cart/clear.js: the image has no such literal. The clear path must use the update endpoint with 0
# quantities, which is what cart/update.js is for.
p = root + r"\StoreFlow.cs"
t = io.open(p, encoding="utf-8").read()
if '"cart/clear.js"' in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace('"cart/clear.js"', '"cart/update.js"'))
    print("StoreFlow.cs        \"cart/clear.js\" -> \"cart/update.js\"")
else:
    print("StoreFlow.cs        no cart/clear.js literal")
