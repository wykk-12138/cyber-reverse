using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1306: the two Unzer decisions the phase-2 notes left as Unknown — the action-URI predicate at
/// <c>0x14094A870</c> and the terminal set behind <c>qword_1472C65A0 + 8</c>.
///
/// <para>
/// Both turned out to be small. The predicate is two <c>IndexOf</c> calls with <c>OrdinalIgnoreCase</c>
/// against <c>unzer.com</c> and <c>heidelpay</c>; the "hash table" is a lazily-built ten-element
/// <c>string[]</c> of failure phrases, filled element by element by <c>sub_14094AB00</c>. The assertions
/// carry the exact strings because the strings are the finding.
/// </para>
/// </summary>
public sealed class UnzerThreeDsDecisionTests
{
    [Theory]
    [InlineData("https://www.unzer.com/threeDS/receiver")]
    [InlineData("https://HEIDELPAY.example/acs")]
    [InlineData("https://payment.heidelpay.com/v1/3ds")]
    public void AUnzerOrHeidelpayHostIsAThreeDsHop(string url)
    {
        Assert.True(UnzerGateway.IsUnzerThreeDsUrl(url));
    }

    [Theory]
    [InlineData("https://shop.topps.com/checkout/success")]
    [InlineData("https://api.stripe.com/v1/payment_intents")]
    [InlineData("")]
    [InlineData(null)]
    public void AnythingElseIsNot(string? url)
    {
        Assert.False(UnzerGateway.IsUnzerThreeDsUrl(url));
    }

    [Fact]
    public void TheTerminalSetIsTheTenPhrasesInTheImage()
    {
        Assert.Equal(10, UnzerGateway.TerminalPhrases.Count);
        Assert.Equal(new[]
        {
            "declined",
            "issue processing your payment",
            "was declined",
            "not authorized",
            "not authorised",
            "refused",
            "insufficient",
            "invalid card",
            "card error",
            "payment error",
        }, UnzerGateway.TerminalPhrases);

        // Both spellings of authorise are present on purpose: one page says "authorized", another
        // "authorised", and the set exists to catch either.
        Assert.Contains("not authorized", UnzerGateway.TerminalPhrases);
        Assert.Contains("not authorised", UnzerGateway.TerminalPhrases);
    }

    [Theory]
    [InlineData("Your card was declined.", true)]
    [InlineData("There was an issue processing your payment", true)]
    [InlineData("The card was DECLINED by the issuer", true)]
    [InlineData("Transaction not authorised", true)]
    [InlineData("insufficient funds", true)]
    [InlineData("Please check your card error code", true)]
    [InlineData("Payment successful, thank you", false)]
    [InlineData("", false)]
    [InlineData(null, false)]
    public void ThePageTextDecides(string? body, bool expected)
    {
        Assert.Equal(expected, UnzerGateway.IsTerminalFailure(body));
    }

    /// <summary>
    /// The behaviour change: a 3DS page that says the card was declined ends the flow there, instead of
    /// being followed and reported as a successful landing.
    /// </summary>
    [Fact]
    public async Task ADeclinedPageStopsTheWalkAndFails()
    {
        using var server = new TinyServer((_, _) =>
            (200, "<html><body>Your card was declined.</body></html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };

        var result = await new UnzerGateway()
            .RunUnzerThreeDsAsync(ctx, server.BaseUrl + "/threeds", null, default);

        Assert.False(result.Ok);
        Assert.Equal("Error verifying payment", result.Error);
        Assert.Equal("true", ctx.Session.Vars["unzer.terminal"]);
        Assert.Contains(ctx.Events, e => e.Name.Contains("terminal failure") && e.Type == "error");
    }

    [Fact]
    public async Task AnOrdinaryPageStillWalks()
    {
        using var server = new TinyServer((_, _) =>
            (200, "<html><body>Authenticating…</body></html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };

        var result = await new UnzerGateway()
            .RunUnzerThreeDsAsync(ctx, server.BaseUrl + "/threeds", null, default);

        Assert.True(result.Ok, result.Error);
        Assert.False(ctx.Session.Vars.ContainsKey("unzer.terminal"));
    }
}
