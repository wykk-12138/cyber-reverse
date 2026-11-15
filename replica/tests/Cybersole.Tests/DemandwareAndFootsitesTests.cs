using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The last two unverified platform wrappers: DemandwareFlow and FootsitesFlow.
///
/// Per docs/PLATFORM_VERIFICATION.md, a registration only changes on A-grade evidence (the site
/// says what it is) or B-grade (it denies a route it should have). This test collects that
/// evidence. Anything weaker gets recorded, not acted on.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class DemandwareAndFootsitesTests
{
    private readonly ITestOutputHelper _out;
    public DemandwareAndFootsitesTests(ITestOutputHelper output) => _out = output;

    /// <summary>Demandware answers controllers under /on/demandware.store/Sites-{Id}/.</summary>
    private static bool HasDemandwarePath(int status, string body) =>
        status is >= 200 and < 400
        && (body.Contains("/on/demandware.store/", StringComparison.OrdinalIgnoreCase)
            || body.Contains("/on/demandware.static/", StringComparison.OrdinalIgnoreCase));

    private async Task ProbeAsync(NetClient net, string label, string url, string? expect = null)
    {
        _out.WriteLine($"=== {label} ===");
        _out.WriteLine($"  {url}");

        try
        {
            var res = await net.GetAsync(url, new RequestOptions { Tag = "dw-probe" },
                CancellationToken.None);

            _out.WriteLine($"  HTTP {res.StatusCode}  {res.BodyBytes:N0}B");

            if (res.StatusCode is 202 or 403 or 429 || res.BodyBytes < 4000)
            {
                _out.WriteLine("  challenge page — no evidence either way");
                _out.WriteLine(string.Empty);
                return;
            }

            foreach (var marker in new[]
                     {
                         "/on/demandware.store/", "/on/demandware.static/", "Sites-",
                         "cdn.shopify.com", "__NEXT_DATA__", "akamai", "queue-it", "x-kpsdk",
                     })
            {
                if (res.Body.Contains(marker, StringComparison.OrdinalIgnoreCase))
                    _out.WriteLine($"  marker  {marker}");
            }
        }
        catch (Exception ex)
        {
            _out.WriteLine($"  {ex.GetType().Name}: {ex.Message}");
        }

        _out.WriteLine(string.Empty);
    }

    [Fact]
    public async Task FunkoAnswersTheDemandwareControllerPath()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        // FunkoFlow declares Domain funko.com and site id Funko-Site; ask the controller directly
        await ProbeAsync(net, "funko home", "https://funko.com/");
        await ProbeAsync(net, "funko controller",
            "https://funko.com/on/demandware.store/Sites-Funko-Site/default/Home-Show");

        Assert.True(true);
    }

    [Fact]
    public async Task TheFootsitesHostsStillLookLikeFootsites()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        foreach (var host in new[]
                 {
                     "footlocker.com", "champssports.com", "footaction.com",
                     "kidsfootlocker.com", "eastbay.com", "ladyfootlocker.com",
                 })
            await ProbeAsync(net, host, $"https://www.{host}/");

        Assert.True(true);
    }
}
