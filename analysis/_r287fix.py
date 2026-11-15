import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''            "CreateTransaction", "GetCheckout", "GetMerchantCode", "GetPayPalToken",
            "GetShippingRate", "GetStructureToken", "ProcessPayment", "SubmitPayment",'''
new = '''            // R287: GetMerchantCode was in this list because structure-token-single wrongly carried it; the literal at
            // 0x034b23a5 has CalculateTaxes at 45 instead. The shared count stays ten.
            "CalculateTaxes", "CreateTransaction", "GetCheckout", "GetPayPalToken",
            "GetShippingRate", "GetStructureToken", "ProcessPayment", "SubmitPayment",'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('expectation updated')
