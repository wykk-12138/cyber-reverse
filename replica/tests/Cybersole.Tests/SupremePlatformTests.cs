using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Is Supreme still the hand-built store SupremeFlow was written for?
///
/// A capture of supremenewyork.com/shop/all showed something that was not there when the flow
/// was written:
///
///   18 requests to us.supreme.com
///    5 requests to otlp-http-production.shopifysvc.com   <- Shopify telemetry
///
/// shopifysvc.com is Shopify's own telemetry host. That is a strong hint the storefront moved to
/// Shopify — which would make SupremeFlow (custom CSRF, colour-id variants, /shop/{id}/add)
/// obsolete, not merely incomplete.
///
/// /cart.js answers 308 for both hosts, so the redirect chain has to be followed before the
/// question can be answered. This test follows it and reports where it lands and what is there.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class SupremePlatformTests
{
    private readonly ITestOutputHelper _out;
    public SupremePlatformTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public async Task TheStorefrontSaysWhichPlatformItIsNow()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var (label, url) in new[]
                 {
                     ("supreme.com cart.js", "https://www.supreme.com/cart.js"),
                     ("supremenewyork.com cart.js", "https://www.supremenewyork.com/cart.js"),
                     ("supreme.com home", "https://www.supreme.com/"),
                     ("shop/all", "https://www.supremenewyork.com/shop/all"),
                 })
        {
            try
            {
                var res = await net.GetAsync(url, new RequestOptions { Tag = "supreme-probe" },
                    CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                var head = res.Body.Length > 100 ? res.Body[..100].Replace('\n', ' ') : res.Body;

                _out.WriteLine($"{label,-28} HTTP {res.StatusCode}  {res.BodyBytes,8:N0}B  [{ct}]");
                _out.WriteLine($"  final url: {res.Url}");
                _out.WriteLine($"  head: {head}");

                foreach (var marker in new[]
                         {
                             "\"token\":", "item_count", "cdn.shopify.com",
                             "shopify-section", "Shopify.theme", "shopifysvc",
                         })
                {
                    if (res.Body.Contains(marker, StringComparison.OrdinalIgnoreCase))
                        _out.WriteLine($"  marker  {marker}");
                }
            }
            catch (Exception ex)
            {
                _out.WriteLine($"{label,-28} {ex.GetType().Name}: {ex.Message}");
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }
}
