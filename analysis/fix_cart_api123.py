import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\PopMartFlow.cs"
t = io.open(p, encoding="utf-8").read()

# There is no GetJsonAsync helper — the flow uses GetAsync for reads.
t = t.replace('''        var res = await GetJsonAsync(c,
            Origin(c.Url) + PopMartEndpoints.ShoppingCartDataList + "cart",
            "popmart-cart-read", ct).ConfigureAwait(false);''',
'''        var res = await GetAsync(c,
            Origin(c.Url) + PopMartEndpoints.ShoppingCartDataList + "cart",
            "popmart-cart-read", ct).ConfigureAwait(false);''', 1)

t = t.replace('''        var res = await GetJsonAsync(c, Origin(c.Url) + PopMartEndpoints.CouponsList,
            "popmart-coupons", ct).ConfigureAwait(false);''',
'''        var res = await GetAsync(c, Origin(c.Url) + PopMartEndpoints.CouponsList,
            "popmart-coupons", ct).ConfigureAwait(false);''', 1)

# Profile has Email and no discount field, so the code comes from the task vars if the runner set one.
t = t.replace('        var code = c.ProfileData?.DiscountCode;',
              '        var code = c.Session.Vars.TryGetValue("discountCode", out var dc) ? dc : null;', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("helpers and discount source corrected")
