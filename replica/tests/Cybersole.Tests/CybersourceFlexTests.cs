using System.Collections.Generic;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1311: Cybersource Flex, the tokenisation between a card and anything Adyen sees.
///
/// <para>
/// The URLs are frozen literals from the image and the constants carry their addresses; the request shape is
/// the vendor's published contract, which is a weaker warrant, so the body assertions read as "this is what
/// we send" rather than "this is what the image sends". The last case is the one that matters most: the flow
/// step must refuse when it has no capture context, because no literal in the image says where one comes from.
/// </para>
/// </summary>
public sealed class CybersourceFlexTests
{
    [Fact]
    public void TheUrlsAreTheLiteralsTheImageHolds()
    {
        Assert.Equal("https://flex.cybersource.com/flex/v2/tokens", CybersourceFlex.TokensUrl);
        Assert.Equal(
            "https://flex.cybersource.com/cybersource/assets/microform/0.11.8/iframe.html?keyId=",
            CybersourceFlex.MicroformIframeV0118);
        Assert.Equal(
            "https://flex.cybersource.com/microform/bundle/v2.0.2/iframe.html?keyId=",
            CybersourceFlex.MicroformIframeV202);
        Assert.Equal("https://api.cybersource.com", CybersourceFlex.ApiHost);
        Assert.Equal("https://secureacceptance.cybersource.com", CybersourceFlex.SecureAcceptanceHost);
        Assert.Equal("/silent/embedded/pay", CybersourceFlex.SecureAcceptancePayPath);
    }

    /// <summary>Two generations of microform are both in the image, so both are reachable here.</summary>
    [Theory]
    [InlineData(true, "https://flex.cybersource.com/microform/bundle/v2.0.2/iframe.html?keyId=abc")]
    [InlineData(false, "https://flex.cybersource.com/cybersource/assets/microform/0.11.8/iframe.html?keyId=abc")]
    public void TheIframeUrlTakesAKeyIdOnEitherGeneration(bool bundleV2, string expected)
    {
        Assert.Equal(expected, CybersourceFlex.MicroformIframeUrl("abc", bundleV2));
    }

    [Fact]
    public void TheMicroformKeyIsEscaped()
    {
        Assert.EndsWith("?keyId=a%2Fb%20c", CybersourceFlex.MicroformIframeUrl("a/b c"));
    }

    [Fact]
    public void TheBodyCarriesTheCardUnderTheKeyTheImageAttests()
    {
        var card = new Card { Number = "4111 1111 1111 1111", Month = "04", Year = "2031", Cvv = "123" };

        var body = CybersourceFlex.TokenizeBody(card);

        Assert.Equal("4111111111111111", body["cardInfo"]!["cardNumber"]!.Value<string>());
        Assert.Equal("04", body["cardInfo"]!["expirationMonth"]!.Value<string>());
        Assert.Equal("2031", body["cardInfo"]!["expirationYear"]!.Value<string>());
        Assert.Equal("123", body["cardInfo"]!["securityCode"]!.Value<string>());
        Assert.NotNull(body["tokenInformation"]);
    }

    [Fact]
    public void AMissingSecurityCodeIsOmittedRatherThanSentEmpty()
    {
        var body = CybersourceFlex.TokenizeBody(new Card { Number = "4111111111111111", Month = "04", Year = "2031" });

        Assert.Null(body["cardInfo"]!["securityCode"]);
    }

    [Fact]
    public async Task TheTokenGetsTheBearerAndTheReplyIsReadBack()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"token\":\"flex-abc\",\"cardType\":\"VISA\"}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            Card = new Card { Number = "4111111111111111", Month = "04", Year = "2031", Cvv = "123" },
        };

        var result = await CybersourceFlex.TokenizeAsync(ctx, "capture-jwt", default, server.BaseUrl + "/flex/v2/tokens");

        Assert.True(result.Ok, result.Error);
        Assert.Equal("flex-abc", result.Token);
        Assert.Equal("VISA", result.CardType);
        Assert.Contains("Bearer capture-jwt", server.RequestHeaders[0]["Authorization"]);
        Assert.Contains("cardInfo", server.Requests[0].Body ?? string.Empty);
    }

    [Theory]
    [InlineData("", "no capture context")]
    [InlineData("   ", "no capture context")]
    public async Task NoCaptureContextIsRefusedBeforeAnyRequest(string capture, string expected)
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.casio.com/",
            Card = new Card { Number = "4111111111111111" },
        };

        var result = await CybersourceFlex.TokenizeAsync(ctx, capture, default);

        Assert.False(result.Ok);
        Assert.Contains(expected, result.Error);
    }

    /// <summary>
    /// The flow step refuses when the session has no capture context, and names the state machine step that
    /// would issue one — because that endpoint is the part the image does not spell out.
    /// </summary>
    [Fact]
    public async Task TheCasioStepSaysWhichStepWouldSupplyTheCaptureContext()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.casio.com/" };

        var outcome = await new CasioFlow().GetPaymentTokenAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("capture context", outcome.Error);
        Assert.Contains("d__37", outcome.Error);
    }

    [Fact]
    public async Task TheCasioStepTokenisesWhenTheSessionCarriesOne()
    {
        using var server = new TinyServer((_, _) => (200, "{\"token\":\"flex-xyz\",\"cardType\":\"MASTERCARD\"}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            Card = new Card { Number = "5555555555554444", Month = "09", Year = "2030", Cvv = "999" },
        };
        ctx.Session.Vars["casio.captureContext"] = "jwt";
        ctx.Session.Vars["casio.flexTokensUrl"] = server.BaseUrl + "/flex/v2/tokens";

        var outcome = await new CasioFlow().GetPaymentTokenAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("flex-xyz", ctx.Session.PaymentToken);
        Assert.Equal("flex-xyz", ctx.Session.Vars["casio.flexToken"]);
        Assert.Equal("MASTERCARD", ctx.Session.Vars["casio.cardType"]);
    }

    /// <summary>A token the session already has is not replaced — the base contract, kept on purpose.</summary>
    [Fact]
    public async Task AnExistingTokenIsLeftAlone()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.casio.com/" };
        ctx.Session.PaymentToken = "already-there";

        var outcome = await new CasioFlow().GetPaymentTokenAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("already-there", ctx.Session.PaymentToken);
    }
}
