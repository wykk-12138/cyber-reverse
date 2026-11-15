using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Is JB Hi-Fi a Shopify store?
///
/// The capture showed <c>/.well-known/shopify/monorail/unstable/produce_batch</c>, which only a
/// Shopify storefront calls. But JbHiFiFlow is a hand-written StoreFlow with its own OAuth
/// (<c>auth.jbhifi.com.au/oauth/token</c>) and its own <c>/api/cart/add</c>.
///
/// Both cannot be right. This asks the decisive question: does /cart.js answer with a Shopify
/// cart object? A large retailer can run Shopify Plus behind custom auth, in which case both
/// observations hold — the storefront is Shopify, the account system is not.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class JbHiFiPlatformTests
{
    private readonly ITestOutputHelper _out;
    public JbHiFiPlatformTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task CartJsSaysWhetherTheStorefrontIsShopify()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var (label, url) in new[]
                 {
                     ("cart.js", "https://www.jbhifi.com.au/cart.js"),
                     ("products.json", "https://www.jbhifi.com.au/products.json?limit=1"),
                 })
        {
            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "jbhifi-probe" },
                    CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                var head = res.Body.Length > 140 ? res.Body[..140].Replace('\n', ' ') : res.Body;

                _out.WriteLine($"{label,-14} HTTP {res.StatusCode}  {res.BodyBytes:N0}B  [{ct}]");
                _out.WriteLine($"  {head}");

                var shopifyCart = res.Body.Contains("\"item_count\"", StringComparison.Ordinal)
                                  || res.Body.Contains("\"token\":\"", StringComparison.Ordinal);
                var shopifyProducts = res.Body.Contains("\"products\":", StringComparison.Ordinal);

                _out.WriteLine($"  shopify cart shape: {shopifyCart}");
                _out.WriteLine($"  shopify products shape: {shopifyProducts}");
            }
            catch (Exception ex)
            {
                _out.WriteLine($"{label,-14} {ex.GetType().Name}: {ex.Message}");
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }
}
