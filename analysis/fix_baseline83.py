import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs"
t = io.open(p, encoding="utf-8").read()

old = ('        "ShippingRatesCreatorView", "SizeCreatorView", "StoreCreatorView", "WebhookCreatorView",')
new = ('        // R83 wired SizeCreatorView and StoreCreatorView: the two preset pages open those\n'
       '        // dialogs instead of hand-building their own copies.\n'
       '        "ShippingRatesCreatorView", "WebhookCreatorView",')

if old not in t:
    raise SystemExit("baseline line not found")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("baseline updated")
