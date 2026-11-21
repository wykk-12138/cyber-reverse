"""Tests pinning the dialect condition."""

import io

TESTS = 'replica/tests/Cybersole.Tests/PayPalPartnerApproveTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheDialectFollowsThePaycode' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1370: the two dialects differ by exactly one declared variable. A payment carrying an encrypted paycode needs
    /// the 5620-character document; everything else takes the 5407-character one. That is a condition on the payment,
    /// which the caller can see, not a per-store list this replica would have had to invent.
    /// </summary>
    [Fact]
    public void TheDialectFollowsThePaycode()
    {
        Assert.Equal(5407, PayPalPartnerApprove.Document.Length);
        Assert.Equal(5620, PayPalPartnerApprove.PaycodeDocument.Length);
        Assert.Equal("paycodeEncrypted", PayPalPartnerApprove.PaycodeVariableName);

        Assert.Same(PayPalPartnerApprove.Document, PayPalPartnerApprove.DocumentFor(false));
        Assert.Same(PayPalPartnerApprove.PaycodeDocument, PayPalPartnerApprove.DocumentFor(true));
    }

    /// <summary>The difference between the two documents is that one name, and nothing else.</summary>
    [Fact]
    public void TheTwoDocumentsDifferByThatOneName()
    {
        var shortDocument = PayPalPartnerApprove.Document;
        var longDocument = PayPalPartnerApprove.PaycodeDocument;

        Assert.DoesNotContain("$paycodeEncrypted", shortDocument);
        Assert.Contains("$paycodeEncrypted", longDocument);
        Assert.Equal(longDocument.Replace("$paycodeEncrypted: String, ", "").Replace("$paycodeEncrypted: String", ""),
            shortDocument.Replace("$selectedAddressId", "$selectedAddressId"));
    }

    /// <summary>The envelope picks the document from the variables it is given.</summary>
    [Fact]
    public void TheEnvelopePicksTheDocumentFromTheVariables()
    {
        var without = PayPalPartnerApprove.EnvelopeFor(new JObject { ["token"] = "t" });
        var with = PayPalPartnerApprove.EnvelopeFor(
            new JObject { ["token"] = "t", ["paycodeEncrypted"] = "enc" });

        Assert.Equal(PayPalPartnerApprove.Document, without["query"]!.ToObject<string>());
        Assert.Equal(PayPalPartnerApprove.PaycodeDocument, with["query"]!.ToObject<string>());
        Assert.Equal("approveMemberPayment", with["operationName"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended three tests')
