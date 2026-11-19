using System.Collections.Generic;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1225: Midtrans' 3-D Secure result completion, decoded from <c>sub_140DA0380</c> (3,886 bytes).
///
/// <para>
/// Nothing of this surface existed in the replica: <c>result-completion</c>, <c>card_token</c> and
/// <c>/v2/3ds/callback</c> all returned no match under <c>replica/src</c> before this round, while the image
/// carries them as frozen literals in one function. The browser block's seven keys are the image's own; its
/// values are the same fingerprint the 3DS2 authenticate form loads, because both functions reference the same
/// string objects.
/// </para>
/// </summary>
public sealed class MidtransThreeDsTests
{
    [Fact]
    public void TheResultCompletionUrlIsTheFrozenPrefixPlusTheTransaction()
    {
        Assert.Equal("https://api.midtrans.com/v2/3ds/result-completion/tx_1",
            MidtransGateway.ResultCompletionUrl("tx_1"));
    }

    [Fact]
    public void TheUrlEscapesTheTransactionId()
    {
        Assert.EndsWith("/a%2Fb", MidtransGateway.ResultCompletionUrl("a/b"));
    }

    [Fact]
    public void TheCallbackPathAndTheTypeLiteralAreTheImagesOnes()
    {
        Assert.Equal("/v2/3ds/callback/", MidtransGateway.ThreeDsCallbackPath);
        Assert.Equal("3ds", MidtransGateway.ThreeDsTypeLiteral);
    }

    [Fact]
    public void TheBrowserBlockCarriesTheSevenFrozenKeys()
    {
        var block = MidtransGateway.ThreeDsBrowserBlock("UA/1");
        Assert.Equal(7, block.Count);
        foreach (var key in new[]
                 {
                     "browserColorDepth", "browserJavaEnabled", "browserLanguage", "browserScreenHeight",
                     "browserScreenWidth", "browserTZ", "browserUserAgent",
                 })
        {
            Assert.True(block.ContainsKey(key), key);
        }
        Assert.Equal("UA/1", block["browserUserAgent"]);
    }

    [Fact]
    public void TheBrowserBlockMatchesTheStripeFingerprintWhereTheyOverlap()
    {
        // both functions load 0x146F9C110/698/750/788/7C8/808/830 — the same seven string objects
        var block = MidtransGateway.ThreeDsBrowserBlock("UA/1");
        foreach (var pair in StripeGateway.BrowserFingerprint)
        {
            if (block.TryGetValue(pair.Key, out var value))
                Assert.Equal(pair.Value, value);
        }
    }
}
