"""R1373: /cartApi/checkout has a sender, and its host is three fragments plus a TLD the image never spells.

R1372's rule paid off immediately: the path had one exact string and one real referencer, and that function's literal
table carries the path, so the hit is a reference rather than a byte pattern. sub_140C32160 holds:

    /cartApi/checkout   CartType   CouponReferences   LineItems   LocationId
    Retail   Shopify    SourceSystem   https://   themeapis   www

So the endpoint is https:// + www + themeapis + <top-level domain> + /cartApi/checkout, and the body carries a cart type
whose two values are Retail and Shopify, plus line items, a location id, a source system and coupon references.

The TLD is not among those eleven literals. Rather than write ".com" for a string the image does not carry, the host is
a caller's value and the class documents the fragments it observed.

Usage: python analysis/add_themeapis_checkout.py
"""
import io

OUT = 'replica/src/Cybersole.Stores/Flows/ThemeApisCheckout.cs'
TESTS = 'replica/tests/Cybersole.Tests/ThemeApisCheckoutTests.cs'

source = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The theme APIs cart checkout endpoint.
///
/// <para>
/// <b>Observed</b> (R1373): <c>sub_140C32160</c> references <c>/cartApi/checkout</c>, <c>CartType</c>,
/// <c>CouponReferences</c>, <c>LineItems</c>, <c>LocationId</c>, <c>SourceSystem</c>, the two cart-type values
/// <c>Retail</c> and <c>Shopify</c>, and the host fragments <c>https://</c>, <c>www</c>, <c>themeapis</c>. The
/// function's literal table carries the path, so the reference is real and not a byte-pattern coincidence.
/// </para>
///
/// <para>
/// <b>Not observed:</b> the top-level domain. Those eleven literals do not include one, so the host is the caller's
/// value; this class will not write ".com" for a string the image does not carry.
/// </para>
/// </summary>
public static class ThemeApisCheckout
{
    /// <summary>The request path.</summary>
    public const string Path = "/cartApi/checkout";

    /// <summary>The scheme the sender writes.</summary>
    public const string Scheme = "https://";

    /// <summary>The subdomain label.</summary>
    public const string SubdomainLabel = "www";

    /// <summary>The host label.</summary>
    public const string HostLabel = "themeapis";

    /// <summary>The two cart types the sender names.</summary>
    public const string CartTypeRetail = "Retail";

    /// <summary>The Shopify cart type.</summary>
    public const string CartTypeShopify = "Shopify";

    /// <summary>The body field names the sender names.</summary>
    public static readonly string[] BodyFieldNames =
    {
        "CartType", "LineItems", "LocationId", "SourceSystem", "CouponReferences",
    };

    /// <summary>
    /// The host the sender would build, given the top-level domain — the one piece its literals do not carry.
    /// </summary>
    public static string HostFor(string topLevelDomain) =>
        Scheme + SubdomainLabel + "." + HostLabel + "." + topLevelDomain.TrimStart('.');

    /// <summary>The full url for a top-level domain.</summary>
    public static string UrlFor(string topLevelDomain) => HostFor(topLevelDomain) + Path;

    /// <summary>
    /// The request body. Only the fields a caller has are written; the sender's own field list is the order.
    /// </summary>
    public static JObject Body(
        string cartType, JArray? lineItems, string? locationId, string? sourceSystem, JArray? couponReferences)
    {
        if (cartType != CartTypeRetail && cartType != CartTypeShopify)
            throw new ArgumentOutOfRangeException(nameof(cartType),
                "cart type is one of the two values the sender names");

        var body = new JObject { ["CartType"] = cartType };
        if (lineItems is not null) body["LineItems"] = lineItems;
        if (!string.IsNullOrEmpty(locationId)) body["LocationId"] = locationId;
        if (!string.IsNullOrEmpty(sourceSystem)) body["SourceSystem"] = sourceSystem;
        if (couponReferences is not null) body["CouponReferences"] = couponReferences;
        return body;
    }

    /// <summary>Post the checkout.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? topLevelDomain, JObject body, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(topLevelDomain))
            return (null, "themeapis: no top-level domain — the image's literals stop at the host label");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(topLevelDomain!), body, "themeapis-checkout", ct)
                .ConfigureAwait(false);
            if (reply is null) return (null, "themeapis: no reply");

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "themeapis: " + ex.GetType().Name);
        }
    }
}
'''

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)

tests = '''using System;
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
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
