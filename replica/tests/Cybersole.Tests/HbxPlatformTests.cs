using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Is HBX actually a Shopify store?
///
/// The registry says so:
/// <code>new FlowStoreModule(new ShopifyFlow("hbx", "HBX", new[] { "hbx.com" }))</code>
///
/// The capture says otherwise: HBX runs its own /api/v2/, sits behind AWS WAF
/// (edge.sdk.awswaf.com), renders client-side, and its product URLs are
/// /{gender}/brands/{brand}/{product} — none of which is Shopify.
///
/// Shopify exposes <c>/products/{handle}.json</c> returning <c>{"product":{...}}</c> and
/// <c>/cart/add.js</c> returning line-item JSON. A storefront that answers those with its SPA
/// shell is not Shopify, and driving it with ShopifyFlow means every cart call hits a page that
/// answers 200 and does nothing.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class HbxPlatformTests
{
    private readonly ITestOutputHelper _out;
    public HbxPlatformTests(ITestOutputHelper output) => _out = output;

    private const string ShopifyProbe =
        "https://hbx.com/products/volley-leather-white-green.json";

    [Fact]
    public async Task HbxDoesNotAnswerShopifyProductJson()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        NetResponse res;
        try
        {
            res = await net.GetAsync(ShopifyProbe, new RequestOptions { Tag = "hbx-shopify-probe" },
                CancellationToken.None);
        }
        catch (Exception ex)
        {
            _out.WriteLine($"unreachable: {ex.GetType().Name}");
            return;
        }

        _out.WriteLine($"GET {ShopifyProbe}");
        _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0} bytes");
        _out.WriteLine($"  content-type {Hdr(res, "content-type")}");

        var head = res.Body.Length > 120 ? res.Body[..120].Replace('\n', ' ') : res.Body;
        _out.WriteLine($"  first 120    {head}");

        // Shopify answers this with a JSON object whose first key is "product"
        var looksLikeShopify = res.Body.TrimStart().StartsWith("{\"product\"", StringComparison.Ordinal)
                               || res.Body.TrimStart().StartsWith("{\n\"product\"", StringComparison.Ordinal);

        _out.WriteLine($"  looks like Shopify product JSON: {looksLikeShopify}");

        if (!looksLikeShopify)
        {
            _out.WriteLine("  -> HBX is NOT Shopify; ShopifyFlow cannot work against it");
            _out.WriteLine("  -> the module registration needs its own flow");
        }

        Assert.False(looksLikeShopify,
            "HBX answered Shopify product JSON — the ShopifyFlow registration would be correct " +
            "after all, and this test's premise is wrong");
    }

    private static string Hdr(NetResponse r, string name) =>
        r.Headers.TryGetValue(name, out var v) ? v : "(absent)";
}
