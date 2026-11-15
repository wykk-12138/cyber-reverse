import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\PopMartFlow.cs"
t = io.open(p, encoding="utf-8").read()

pairs = [
    ('Origin(c.Url) + "/api/stock"', "Origin(c.Url) + PopMartEndpoints.ProductDetails"),
    ('Origin(c.Url) + "/api/cart/add"', "Origin(c.Url) + PopMartEndpoints.AddBoxListToCart"),
    ('Origin(c.Url) + "/api/order/submit"', "Origin(c.Url) + PopMartEndpoints.BuyNow"),
]

for old, new in pairs:
    print(("found   " if old in t else "missing "), old[:44])
    t = t.replace(old, new)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("PopMartFlow rewritten to the image's family")
