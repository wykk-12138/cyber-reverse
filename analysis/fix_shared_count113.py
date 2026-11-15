import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("public void TheStructureTokenFlowsShareNineSteps()",
              "public void TheStructureTokenFlowsShareTenSteps()", 1)

old = """        // eight names are shared: the payment engine's spine
        Assert.Equal(8, shared.Count);
        Assert.Contains("GetStructureToken", shared);"""
new = """        // ten names are shared: the payment engine's spine. The count is read from the two lists,
        // not hand-counted — a hand count here was wrong twice (8, then "nine" in the test name).
        Assert.Equal(10, shared.Count);
        Assert.Equal(new[]
        {
            "CreateTransaction", "GetCheckout", "GetMerchantCode", "GetPayPalToken",
            "GetShippingRate", "GetStructureToken", "ProcessPayment", "SubmitPayment",
            "SubmitPayPal", "SubmitShipping",
        }, shared);"""
if old not in t:
    raise SystemExit("count anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("shared count corrected to 10, with the set pinned")
