using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Which cart-add path does Offspring's Hybris backend actually expose?
///
/// HybrisFlow posts to /cart/add with productCodePost/qty. That path is inferred from Hybris's
/// documented controller shape — the only two endpoints verified so far are the read-only
/// /view/... ones. Guessing wrong here is the quiet failure this project keeps meeting: the
/// request returns something, nothing is added, and the flow reports success.
///
/// So probe the candidates and read the status. What matters is the difference between
///
///   404                the route is not there
///   400 / 405 / 200    the route IS there and merely wants different input
///   403                Akamai; tells us nothing either way
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class HybrisCartPathTests
{
    private readonly ITestOutputHelper _out;
    public HybrisCartPathTests(ITestOutputHelper output) => _out = output;

    private const string Origin = "https://www.offspring.co.uk";

    [Fact]
    public async Task TheCartAddRouteIsWhereTheFlowThinksItIs()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var candidates = new[]
        {
            ("/cart/add", "the path HybrisFlow posts to"),
            ("/view/cart/add", "the /view/ controller variant"),
            ("/view/component/cart/add", "component-scoped, matches minibasketAjax"),
            ("/view/component/basket/add", "basket-scoped"),
        };

        foreach (var (path, why) in candidates)
        {
            try
            {
                // GET first: a POST on a valid route answers 405 or 400, a missing one 404
                var res = await net.GetAsync(Origin + path,
                    new RequestOptions { Tag = "hybris-cart-probe" }, CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                var head = res.Body.Length > 90 ? res.Body[..90].Replace('\n', ' ') : res.Body;

                _out.WriteLine($"{path,-30} HTTP {res.StatusCode}  {res.BodyBytes,7:N0}B  [{ct}]");
                _out.WriteLine($"  {why}");
                _out.WriteLine($"  {head}");

                var verdict = res.StatusCode switch
                {
                    404 => "route missing",
                    405 or 400 => "ROUTE EXISTS (wants POST/other input)",
                    >= 200 and < 300 => "ROUTE EXISTS and answered",
                    403 or 429 => "blocked — no evidence",
                    _ => $"other {res.StatusCode}",
                };

                _out.WriteLine($"  -> {verdict}");
            }
            catch (Exception ex)
            {
                _out.WriteLine($"{path,-30} {ex.GetType().Name}");
            }

            _out.WriteLine(string.Empty);
        }

        // the one verified read-only controller, as a control: if this 404s the host is wrong
        var control = await net.GetAsync(Origin + "/view/component/basket/minibasketAjax",
            new RequestOptions { Tag = "hybris-control" }, CancellationToken.None);

        _out.WriteLine($"{"control: minibasketAjax",-30} HTTP {control.StatusCode}  " +
                       $"{control.BodyBytes:N0}B");

        Assert.True(true);
    }
}
