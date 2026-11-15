import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\ServiceHosts.cs"
t = io.open(p, encoding="utf-8").read()

# ScheelsFrontastic lives in RetailApiFamilies, so it needs its outer class name.
fixes = [
    ('["Login"] = ScheelsFrontastic.Login', '["Login"] = RetailApiFamilies.ScheelsFrontastic.Login'),
    ('["GetProduct"] = ScheelsFrontastic.GetProduct',
     '["GetProduct"] = RetailApiFamilies.ScheelsFrontastic.GetProduct'),
    ('["AddToCart"] = ScheelsFrontastic.AddToCart',
     '["AddToCart"] = RetailApiFamilies.ScheelsFrontastic.AddToCart'),
    ('["Checkout"] = ScheelsFrontastic.Checkout',
     '["Checkout"] = RetailApiFamilies.ScheelsFrontastic.Checkout'),
    ('["CompleteDetailsCheckout"] = ScheelsFrontastic.CompleteDetailsCheckout',
     '["CompleteDetailsCheckout"] = RetailApiFamilies.ScheelsFrontastic.CompleteDetailsCheckout'),
    ('["SignifydStepUpCode"] = ScheelsFrontastic.SignifydStepUpCode',
     '["SignifydStepUpCode"] = RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode'),
    ('["CompleteSignifydStepUp"] = ScheelsFrontastic.CompleteSignifydStepUp',
     '["CompleteSignifydStepUp"] = RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp'),
]

for old, new in fixes:
    if old not in t:
        print("skip:", old[:40])
        continue
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("qualified the Frontastic references")
