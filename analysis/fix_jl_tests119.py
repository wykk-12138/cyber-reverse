import io

# 1) the flow count test: 17 -> 19 for John Lewis
p1 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs"
t1 = io.open(p1, encoding="utf-8").read()
old1 = "        Assert.Equal(17, StoreFlowSteps.JohnLewis.Count);"
new1 = "        Assert.Equal(19, StoreFlowSteps.JohnLewis.Count);   // R119: FindProduct 21 + AddToCart 22"
if old1 not in t1:
    raise SystemExit("JL count anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))
print("flow count: 19")

# 2) the unmapped test: three page/Stripe steps plus the two cart-side steps
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\JohnLewisStepMapTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        Assert.Equal(3, JohnLewisStepMap.UnmappedSteps.Count);
        Assert.Contains("GetHome", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("HandleRequiresAction", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("GetStripePaymentIntent", JohnLewisStepMap.UnmappedSteps);'''

new2 = '''        // five, not three: R119 added FindProduct(21) and AddToCart(22) to the flow, and the BFF has
        // no cart endpoints at all — it starts at the handover.
        Assert.Equal(5, JohnLewisStepMap.UnmappedSteps.Count);
        Assert.Contains("GetHome", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("FindProduct", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("AddToCart", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("HandleRequiresAction", JohnLewisStepMap.UnmappedSteps);
        Assert.Contains("GetStripePaymentIntent", JohnLewisStepMap.UnmappedSteps);'''

if old2 not in t2:
    raise SystemExit("unmapped anchor missing")
t2 = t2.replace(old2, new2, 1)

# the "more steps than endpoints" test also quoted 17 in prose; keep the numbers it asserts correct
t2 = t2.replace("/// John Lewis's seventeen steps against its twelve BFF endpoints.",
                "/// John Lewis's nineteen steps against its twelve BFF endpoints.", 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("unmapped: 5")
