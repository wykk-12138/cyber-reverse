import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"
t = io.open(p, encoding="utf-8").read()

# R94: three of the four controllers the flow called are not in the image at all.
pairs = [
    ('Controller(c, "Cart-Show")', 'Controller(c, DemandwareControllers.CartGet)'),
    ('Controller(c, "Cart-AddProduct")', 'Controller(c, DemandwareControllers.CartAddProduct)'),
    ('Controller(c, "Checkout-Begin")', 'Controller(c, DemandwareControllers.CheckoutBegin)'),
    ('Controller(c, "Checkout-SubmitShipping")', 'Controller(c, DemandwareControllers.SubmitShipping)'),
    ('Controller(c, "Checkout-SubmitPayment")', 'Controller(c, DemandwareControllers.SubmitPayment)'),
    ('Controller(c, "Checkout-Submit")', 'Controller(c, DemandwareControllers.PlaceOrder)'),
]

for old, new in pairs:
    if old not in t:
        print("skip (not present):", old)
        continue
    t = t.replace(old, new)
    print("replaced:", old)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("DemandwareFlow now uses the image's controller names")
