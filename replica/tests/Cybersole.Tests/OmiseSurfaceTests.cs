using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1246: what the image actually carries for Omise, and what the replica had assumed.
///
/// <para>
/// Searching the binary for <c>omise</c> returns eight hits, all of them inside the word "Promise", which is exactly
/// the kind of near-miss that has produced false positives in earlier rounds. The real literals only appear when the
/// search includes the host: <c>https://checkout-page.omise.co/</c> (0x14705CD0C),
/// <c>https://checkout-page.omise.co/api/payment</c> (0x14705CD64) and
/// <c>https://checkout-page.omise.co/api/sessions/</c> (0x14705CDD4). <c>api.omise.co</c> has no hit at all.
/// </para>
/// </summary>
public sealed class OmiseSurfaceTests
{
    [Fact]
    public void TheHostedCheckoutRootIsTheImagesLiteralIncludingTheTrailingSlash()
    {
        Assert.Equal("https://checkout-page.omise.co/", OmiseGateway.CheckoutPageUrl);
    }

    [Fact]
    public void TheSessionsEndpointIsNowPresent()
    {
        Assert.Equal("/api/sessions/", OmiseGateway.SessionsPath);
        Assert.Equal("https://checkout-page.omise.co/api/sessions/sess_1", OmiseGateway.SessionsUrl("sess_1"));
    }

    [Fact]
    public void TheHostTheImageAttestsIsTheCheckoutOne()
    {
        // the tokenising host api.omise.co has zero hits in the image; this pins the one that does
        Assert.Equal("https://checkout-page.omise.co", OmiseGateway.CheckoutHost);
        Assert.StartsWith(OmiseGateway.CheckoutHost, OmiseGateway.SessionsUrl("x"));
    }

    [Fact]
    public void TheSessionIdIsEscaped()
    {
        Assert.EndsWith("/a%2Fb", OmiseGateway.SessionsUrl("a/b"));
    }
}
