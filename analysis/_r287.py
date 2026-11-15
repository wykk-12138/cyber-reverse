import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs'
t = io.open(p, encoding='utf-8').read()

old = '''        new Step("EditLine", 34), new Step("AddToCart", 35), new Step("GetCheckout", 36),
        new Step("GetMerchantCode", 37), new Step("GetShippingRate", 38),
        new Step("SubmitShipping", 39), new Step("GetStructureToken", 40),
        new Step("CreateTransaction", 41), new Step("SubmitPayment", 42),
        new Step("GetPayPalToken", 43), new Step("SubmitPayPal", 44),
        new Step("ProcessPayment", 45),'''
new = '''        // R287: the list here had GetMerchantCode at 37 and no CalculateTaxes, and the ordinals were 34–45. The literal at
        // 0x034b23a5 says otherwise, and its own lambda table (b__43_1 GetShippingRate, b__44_1 SubmitShipping,
        // b__45_1 CalculateTaxes, b__46_1 GetStructureToken …) agrees with it step for step:
        //   EditLine 40, AddToCart 41, GetCheckout 42, GetShippingRate 43, SubmitShipping 44, CalculateTaxes 45,
        //   GetStructureToken 46, CreateTransaction 47, SubmitPayment 48, GetPayPalToken 49, SubmitPayPal 50,
        //   ProcessPayment 51
        // GetMerchantCode is not a step of this flow — it belongs to structure-token-multi at ordinal 38.
        new Step("EditLine", 40), new Step("AddToCart", 41), new Step("GetCheckout", 42),
        new Step("GetShippingRate", 43), new Step("SubmitShipping", 44),
        new Step("CalculateTaxes", 45), new Step("GetStructureToken", 46),
        new Step("CreateTransaction", 47), new Step("SubmitPayment", 48),
        new Step("GetPayPalToken", 49), new Step("SubmitPayPal", 50),
        new Step("ProcessPayment", 51),'''
assert old in t
t = t.replace(old, new, 1)

# the doc comment above it also stated a wrong ordinal
t = t.replace('/// carrying <c>GetStructureToken</c> at ordinal 40 instead of 42.',
              '/// carrying <c>GetStructureToken</c> at ordinal 46 and <c>CalculateTaxes</c> at 45.', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('structure-token-single corrected from the literal at 0x034b23a5')
