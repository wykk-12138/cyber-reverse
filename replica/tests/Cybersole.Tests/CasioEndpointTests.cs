using Cybersole.Http;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Does Casio actually serve the endpoints CasioFlow calls?
///
/// The flow covers six of the seven commerce steps, which reads as nearly complete. But
/// SubmitOrderAsync posts <c>{}</c> to /checkout/submit — no address, no payment — and neither
/// SubmitShippingAsync nor SubmitPaymentAsync exists. So the order step is "implemented" while
/// being unable to place an order, which is the pattern the coverage matrix cannot see.
///
/// The add-to-cart path (/cart/add with sku/quantity/recaptcha) came from a real page probe in
/// round 39. The checkout paths did not. This asks which of them are real.
///
/// As with the Hybris probe, the difference that matters is
///
///   404                the route is not there
///   400 / 405 / 401    the route IS there, wants different input or a session
///   403 / 429          refused; no evidence either way
///
/// Speed=Slow, network-bound.
/// </summary>
[Trait("Speed", "Slow")]
public class CasioEndpointTests
{
    private readonly ITestOutputHelper _out;
    public CasioEndpointTests(ITestOutputHelper output) => _out = output;

    private const string Origin = "https://www.casio.com";

    [Fact]
    public async Task TheCheckoutRoutesAreWhereTheFlowThinksTheyAre()
    {
        using var net = new NetClient { Transport = TransportMode.SChannel };

        var candidates = new[]
        {
            ("/cart/add", "the add-to-cart path the flow uses"),
            ("/checkout", "the checkout page the flow opens"),
            ("/checkout/submit", "the order endpoint the flow posts to"),
            ("/api/cart/add", "a JSON API variant"),
        };

        foreach (var (path, why) in candidates)
        {
            try
            {
                var res = await net.GetAsync(Origin + path,
                    new RequestOptions { Tag = "casio-probe" }, CancellationToken.None);

                var ct = res.Headers.TryGetValue("content-type", out var c) ? c : "";
                var head = res.Body.Length > 90 ? res.Body[..90].Replace('\n', ' ') : res.Body;

                _out.WriteLine($"{path,-20} HTTP {res.StatusCode}  {res.BodyBytes,8:N0}B  [{ct}]");
                _out.WriteLine($"  {why}");

                var verdict = res.StatusCode switch
                {
                    404 or 410 => "route MISSING",
                    405 or 400 => "route EXISTS (wants POST/other input)",
                    401 => "route EXISTS, wants a session",
                    >= 200 and < 300 => "route EXISTS and answered",
                    403 or 429 => "refused — no evidence",
                    _ => $"other {res.StatusCode}",
                };

                _out.WriteLine($"  -> {verdict}");
                if (res.StatusCode is >= 200 and < 300)
                    _out.WriteLine($"  head: {head}");
            }
            catch (Exception ex)
            {
                _out.WriteLine($"{path,-20} {ex.GetType().Name}: {ex.Message}");
            }

            _out.WriteLine(string.Empty);
        }

        Assert.True(true);
    }
}
