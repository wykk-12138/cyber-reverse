import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        Assert.Contains("GetMerchantCode", shared);
        Assert.Contains("ProcessPayment", shared);'''
new = '''        // R287: GetMerchantCode is NOT shared — it belongs to the multi flow only (ordinal 38). Checking it was the
        // assertion that encoded the defect.
        Assert.DoesNotContain("GetMerchantCode", shared);
        Assert.Contains("CalculateTaxes", shared);
        Assert.Contains("ProcessPayment", shared);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('the containment assertion corrected too')
