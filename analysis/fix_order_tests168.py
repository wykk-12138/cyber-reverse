import io

# 1) the mobile marker matches the code: BodyJs() takes no argument
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = 'new Step(4, "mobile", "MobileSurface.BodyJs(userAgent)",'
new1 = 'new Step(4, "mobile", "MobileSurface.BodyJs()",'

if old1 not in t1:
    raise SystemExit("mobile marker anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) the rule assertion looked for a substring the sentence does not contain in that form
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        Assert.Contains("position is semantics", SurfaceOrder.Rule);
        Assert.Contains("install, orders, deletes or masks", SurfaceOrder.Rule);'''

new2 = '''        Assert.Contains("position is semantics", SurfaceOrder.Rule);
        Assert.Contains("installs, orders, deletes or masks", SurfaceOrder.Rule);
        Assert.Contains("where its verb allows", SurfaceOrder.Rule);'''

if old2 not in t2:
    raise SystemExit("rule anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))

print("marker and rule assertion corrected")
