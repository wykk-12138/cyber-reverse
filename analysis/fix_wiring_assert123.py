import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\PopMartCartWiringTests.cs"
t = io.open(p, encoding="utf-8").read()

# The flow file references the constants, not their literal values.
old = '''        Assert.Contains("GetCartAsync", flow);
        Assert.Contains(PopMartEndpoints.ShoppingCartDataList, flow);
        Assert.Contains(PopMartEndpoints.CouponsList, flow);
        Assert.Contains(PopMartEndpoints.CouponsVerify, flow);'''

new = '''        Assert.Contains("GetCartAsync", flow);
        Assert.Contains("PopMartEndpoints.ShoppingCartDataList", flow);
        Assert.Contains("PopMartEndpoints.CouponsList", flow);
        Assert.Contains("PopMartEndpoints.CouponsVerify", flow);

        // and the constants resolve to the /shop/v1 paths this session recorded
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.ShoppingCartDataList);
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.CouponsList);
        Assert.StartsWith("/shop/v1/", PopMartEndpoints.CouponsVerify);'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertion now checks the constant names")
