using System.Collections.Generic;
using System.IO;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R203: the Shopify identifier block. Two clusters — header names spelled like headers, and a lower-case cluster the
/// image gives no role for. This pins which is which, by address.
/// </summary>
public sealed class ShopifyHeadersTests
{
    private readonly ITestOutputHelper _out;
    public ShopifyHeadersTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Pool() =>
        File.ReadAllText(Path.Combine(Path.GetDirectoryName(Root())!, "analysis", "pe_strings.txt"));

    [Fact]
    public void EveryLiteralIsInTheImageAtItsAddress()
    {
        var pool = Pool();
        foreach (var literal in ShopifyHeaders.All)
        {
            Assert.True(pool.Contains(literal.Address + "  " + literal.Value, System.StringComparison.Ordinal),
                $"{literal.Value} is not at {literal.Address}");
        }

        Assert.Equal(8, ShopifyHeaders.All.Count());
        _out.WriteLine($"{ShopifyHeaders.Headers.Count} headers, {ShopifyHeaders.Tags.Count} tags");
    }

    [Fact]
    public void TheTwoSpellingsAreTheSameHeader()
    {
        // HTTP header names are case-insensitive, and the image writes this one both ways
        Assert.Equal(ShopifyHeaders.StorefrontAccessToken,
            ShopifyHeaders.StorefrontAccessTokenLower, ignoreCase: true);
        Assert.NotEqual(ShopifyHeaders.StorefrontAccessToken, ShopifyHeaders.StorefrontAccessTokenLower);
    }

    [Fact]
    public void TheTagClusterIsNotAHeaderList()
    {
        // a header spelled in lower case with no X- prefix would be the odd one out in this image, and three of these
        // four are exactly what the replica writes into its own request log
        foreach (var tag in ShopifyHeaders.TraceTags)
        {
            Assert.DoesNotContain("X-", tag);
            Assert.StartsWith("shopify-", tag, System.StringComparison.Ordinal);
        }

        // and the one entry whose role is unresolved is not offered as a tag
        Assert.DoesNotContain(ShopifyHeaders.IdentificationSignature, ShopifyHeaders.TraceTags);
        Assert.DoesNotContain(ShopifyHeaders.TapPayHost, ShopifyHeaders.TraceTags);
    }

    [Fact]
    public void TheSignatureFieldAlsoAppearsInTheImagesJs()
    {
        // the name is not free-floating: the checkout form's own JS names its payment fields the same way
        Assert.Contains("0x03376901  " + ShopifyHeaders.SignatureFieldInJs, Pool(), System.StringComparison.Ordinal);
    }

    [Fact]
    public void TheFlowUsesTheTable()
    {
        var flow = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Stores", "Flows", "ShopifyFlow.cs"));

        Assert.Contains("ShopifyHeaders.StorefrontAccessToken", flow, System.StringComparison.Ordinal);
        Assert.Contains("ShopifyHeaders.CheckoutClientTag", flow, System.StringComparison.Ordinal);
        Assert.Contains("ShopifyHeaders.CheckoutSourceTag", flow, System.StringComparison.Ordinal);

        // the inline spellings are gone, so there is one place to change
        Assert.DoesNotContain("\"X-Shopify-Storefront-Access-Token\"", flow);
        Assert.DoesNotContain("\"shopify-checkout-init\"", flow);
    }
}
