"""Correct the AddressInput docstring after checking the sender's literal set, and pin the correction.

R1372 first wrote that addressLine1/addressLine2/recipientName each had a code reference, on the strength of
disp32_scan_any hits. Decoding the CreditCard sender's full literal list refutes that for addressLine2: the function at
0x140AAE300 references twenty literals and none of them is an address field. So a disp32 hit is a byte pattern, not a
reference, until the function's own literal set contains it.

What survives: the four names exist in the image's string table. What does not: that they form one construction here.
"""
import io
import re

MODEL = 'replica/src/Cybersole.Stores/Flows/AddressInput.cs'
TESTS = 'replica/tests/Cybersole.Tests/AddressInputTests.cs'

text = io.open(MODEL, encoding='utf-8').read()

old_para = '''/// <b>Observed</b> (R1372): the image keeps <c>recipientName</c>, <c>addressLine1</c>, <c>addressLine2</c> and
/// <c>locality</c> as strings, and code references the first three (0x140AD5FAD, 0x140A42650, 0x140AAEA55). The
/// type name itself is not a string anywhere, which is why the documents' <c>AddressInput!</c> annotation could not
/// be resolved from the name alone.'''

new_para = '''/// <b>Observed</b> (R1372): the image keeps <c>recipientName</c> (0x147149A94), <c>addressLine1</c> (0x146F6EC6C),
/// <c>addressLine2</c> (0x146F6EC9C) and <c>locality</c> (0x146FC9852) as strings. The type name itself is not a
/// string anywhere, which is why the documents' <c>AddressInput!</c> annotation could not be resolved from the name.
///
/// <para>
/// <b>Refuted in the same round:</b> the first reading claimed code references for three of them on the strength of
/// disp32 byte-pattern hits. Decoding the referenced function's own literal list showed twenty literals and not one
/// address field, so a disp32 hit is a pattern until the function's literal set contains the name. What remains is
/// the four strings, not a construction.'''

if old_para not in text:
    raise SystemExit('docstring paragraph not found as written')
text = text.replace(old_para, new_para)
io.open(MODEL, 'w', encoding='utf-8', newline='').write(text)
print('docstring corrected')

tests = io.open(TESTS, encoding='utf-8').read()
if 'TheNamesSurviveButTheReferenceClaimDoesNot' not in tests:
    block = '''
    /// <summary>
    /// R1372: the four names are in the image's string table; a claim that three of them are referenced was withdrawn
    /// after the referenced function's literal list contained none of them. This test records the distinction so the
    /// next reader does not inherit the over-claim.
    /// </summary>
    [Fact]
    public void TheNamesSurviveButTheReferenceClaimDoesNot()
    {
        Assert.Equal(4, AddressInput.ModernFieldNames.Length);
        Assert.Contains("recipientName", AddressInput.ModernFieldNames);
        Assert.Contains("addressLine1", AddressInput.ModernFieldNames);
        Assert.Contains("addressLine2", AddressInput.ModernFieldNames);
        Assert.Contains("locality", AddressInput.ModernFieldNames);

        // The CreditCard sender's twenty literals, decoded in this round: no address field among them.
        Assert.DoesNotContain("addressLine1", new[]
        {
            " ", "/finalize", "CreditCard", "Submit order", "api/checkout/v1/orders/", "application/json",
            "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName", "cardNumber", "paymentMethodId",
            "paymentMethodType", "savePaymentMethodAsToken",
        });
    }
}
'''
    tests = tests.rstrip()
    tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
    print('added the correction test')
