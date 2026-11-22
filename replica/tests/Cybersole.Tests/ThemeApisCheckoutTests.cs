using System;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1373: the cart checkout endpoint's sender. The path, the body fields and the two cart types are observed; the
/// top-level domain is not, and this pins that it stays the caller's rather than being guessed.
/// </summary>
public sealed class ThemeApisCheckoutTests
{
    [Fact]
    public void ThePathAndFragmentsAreTheObservedOnes()
    {
        Assert.Equal("/cartApi/checkout", ThemeApisCheckout.Path);
        Assert.Equal("https://", ThemeApisCheckout.Scheme);
        Assert.Equal("www", ThemeApisCheckout.SubdomainLabel);
        Assert.Equal("themeapis", ThemeApisCheckout.HostLabel);
        Assert.Equal("Retail", ThemeApisCheckout.CartTypeRetail);
        Assert.Equal("Shopify", ThemeApisCheckout.CartTypeShopify);
        Assert.Equal(new[] { "CartType", "LineItems", "LocationId", "SourceSystem", "CouponReferences" },
            ThemeApisCheckout.BodyFieldNames);
    }

    [Fact]
    public void TheHostIsBuiltFromTheFragmentsAndTheCallersDomain()
    {
        Assert.Equal("https://www.themeapis.example/cartApi/checkout", ThemeApisCheckout.UrlFor("example"));
        Assert.Equal("https://www.themeapis.example/cartApi/checkout", ThemeApisCheckout.UrlFor(".example"));
    }

    /// <summary>Only the two cart types the sender names are accepted.</summary>
    [Fact]
    public void OnlyTheTwoCartTypesAreAccepted()
    {
        var shopify = ThemeApisCheckout.Body(ThemeApisCheckout.CartTypeShopify, null, "loc-1", null, null);
        Assert.Equal("Shopify", shopify["CartType"]!.ToObject<string>());
        Assert.Equal("loc-1", shopify["LocationId"]!.ToObject<string>());
        Assert.Null(shopify["LineItems"]);

        Assert.Throws<ArgumentOutOfRangeException>(
            () => ThemeApisCheckout.Body("Wholesale", null, null, null, null));
    }
}
