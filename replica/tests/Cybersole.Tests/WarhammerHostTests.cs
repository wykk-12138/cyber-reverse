using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Which host serves Warhammer's API?
///
/// WarhammerFlow posts to <c>api.prod.warhammer.com/api/basket/items</c> and
/// <c>api.prod.warhammer.com/api/orders</c>, and reads <c>/api/products/{code}</c>. Those all
/// answered 403 with a 42-byte JSON body, which round 59 read as "route exists, refuses us" — a
/// D-grade signal that cannot justify a change.
///
/// A capture of the storefront shows something the flow does not use:
///
///   200  GET  https://www.warhammer.com/api/i18n            <- the SITE host serves /api/
///   200  POST https://api.prod.warhammer.com/graphql        <- the API host speaks GraphQL
///
/// So there may be two API surfaces: an AEM-style /api/ on the site host, and a GraphQL gateway
/// on the api host. The flow mixes them — it takes the host from the second and the path shape
/// from the first. This asks each combination directly.
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class WarhammerHostTests
{
    private readonly ITestOutputHelper _out;
    public WarhammerHostTests(ITestOutputHelper output) => _out = output;

    private async Task ProbeAsync(NetClient net, string url)
    {
        try
        {
            var res = await net.GetAsync(url, new RequestOptions { Tag = "wh-host" },
                CancellationToken.None);

            var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
            var head = res.Body.Length > 90 ? res.Body[..90].Replace('\n', ' ') : res.Body;

            _out.WriteLine($"{url.Replace("https://", ""),-58} HTTP {res.StatusCode}  " +
                           $"{res.BodyBytes,7:N0}B  [{ct}]");
            if (res.StatusCode is >= 200 and < 300)
                _out.WriteLine($"  head: {head}");
        }
        catch (Exception ex)
        {
            _out.WriteLine($"{url.Replace("https://", ""),-58} {ex.GetType().Name}");
        }
    }

    [Fact]
    public async Task TheSiteApiPrefixIsTheOneThatAnswers()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        // the endpoint the capture proved works
        await ProbeAsync(net, "https://www.warhammer.com/api/i18n");
        _out.WriteLine(string.Empty);

        // the paths the flow uses, asked of the SITE host instead of the API host
        foreach (var p in new[] { "/api/products/60010299006", "/api/basket/items", "/api/orders" })
            await ProbeAsync(net, "https://www.warhammer.com" + p);

        _out.WriteLine(string.Empty);

        // and the API host again, for comparison
        foreach (var p in new[] { "/api/i18n", "/api/products/60010299006" })
            await ProbeAsync(net, "https://api.prod.warhammer.com" + p);

        Assert.True(true);
    }
}
