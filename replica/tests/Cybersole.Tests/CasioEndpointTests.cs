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

}
