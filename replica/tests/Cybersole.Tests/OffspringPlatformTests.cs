using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// What platform is Offspring actually on?
///
/// OffspringFlow currently derives from MagentoFlow, but no Magento surface ever answered:
/// /rest/V1/store/storeConfigs is 404, /customer/section/load/ is 404, /cart.js is 404.
///
/// A capture of the home page shows what it does call:
///
///   GET /akam/13/710368ee                        (Akamai Bot Manager)
///   GET /view/resources/getUserInfo
///   GET /view/component/basket/minibasketAjax
///
/// The /view/... shape is the one thing that matters here: it is not Magento, not Shopify and
/// not Demandware. This test records the evidence per host so the registration can be decided
/// on what answers rather than on what does not.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class OffspringPlatformTests
{
    private readonly ITestOutputHelper _out;
    public OffspringPlatformTests(ITestOutputHelper output) => _out = output;

    private async Task ProbeAsync(NetClient net, string label, string url)
    {
        try
        {
            var res = await net.GetAsync(url, new RequestOptions { Tag = "os-probe" },
                CancellationToken.None);

            var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
            var head = res.Body.Length > 120 ? res.Body[..120].Replace('\n', ' ') : res.Body;

            _out.WriteLine($"{label,-26} HTTP {res.StatusCode}  {res.BodyBytes:N0}B  [{ct}]");
            _out.WriteLine($"  {head}");

            foreach (var marker in new[]
                     {
                         "Magento_", "mage/cookies", "static/version",
                         "cdn.shopify.com", "shopify-section",
                         "/on/demandware.store/", "__NEXT_DATA__",
                         "require.config", "hybris", "/view/",
                     })
            {
                if (res.Body.Contains(marker, StringComparison.OrdinalIgnoreCase))
                    _out.WriteLine($"  marker  {marker}");
            }
        }
        catch (Exception ex)
        {
            _out.WriteLine($"{label,-26} {ex.GetType().Name}: {ex.Message}");
        }

        _out.WriteLine(string.Empty);
    }

    [Fact]
    public async Task TheHomePageShowsWhatBackendItUses()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        await ProbeAsync(net, "offspring home", "https://www.offspring.co.uk/");
        await ProbeAsync(net, "minibasket", "https://www.offspring.co.uk/view/component/basket/minibasketAjax");
        await ProbeAsync(net, "userinfo", "https://www.offspring.co.uk/view/resources/getUserInfo");

        Assert.True(true);
    }
}
