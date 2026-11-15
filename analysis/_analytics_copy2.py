import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        ["OutForDelivery"] = "Out for delivery",   // Checkout.OutForDelivery'''
new = '''        ["OutForDelivery"] = "Out for delivery",   // Checkout.OutForDelivery
        ["ScheduledDelivery"] = "Scheduled Delivery",   // Checkout.ScheduledDelivery'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('ScheduledDelivery added')
