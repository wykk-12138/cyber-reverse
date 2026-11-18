using System.Collections.Generic;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1127: John Lewis's <c>GetPaymentPage</c>.
///
/// The image calls <c>v2/orderforms/payment-page</c> with two verbs — a GET at site 0x140a3ff44
/// (verb slot 0x1408b61e0, called at 0x140a3ff75) and a PUT at 0x140a4003b (slot 0x1408b6310,
/// called at 0x140a4006f). This step is the read, so these facts pin the GET: it must reach the
/// flow's own BFF URL rather than the base class's <c>Origin + "/payments"</c> fallback, and leave the
/// answer where both key spellings can find it.
/// </summary>
public sealed class JohnLewisPaymentPageTests
{
    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://www.johnlewis.com/ourshop/product",
        Shipping = new Address { Country = "GB" },
    };

    [Fact]
    public async Task ThePaymentPageIsReadWithGetFromTheBffPath()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod);
            return (200, "{\"paymentPage\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["jl.paymentPageUrl"] = server.BaseUrl + "/bff/v2/orderforms/payment-page";

        var outcome = await new JohnLewisFlow().GetPaymentPageAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("GET", request);
        Assert.Contains("/bff/v2/orderforms/payment-page", request);
    }

    [Fact]
    public async Task TheAnswerIsKeptUnderBothSpellings()
    {
        using var server = new TinyServer((_, _) => (200, "{\"methods\":[\"CARD\"]}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["jl.paymentPageUrl"] = server.BaseUrl + "/bff/v2/orderforms/payment-page";

        var outcome = await new JohnLewisFlow().GetPaymentPageAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("{\"methods\":[\"CARD\"]}", ctx.Session.Vars["jl.paymentPageBody"]);
        Assert.Equal("{\"methods\":[\"CARD\"]}", ctx.Session.Vars["paymentPage"]);
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (503, "nope"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["jl.paymentPageUrl"] = server.BaseUrl + "/bff/v2/orderforms/payment-page";

        var outcome = await new JohnLewisFlow().GetPaymentPageAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }

    /// <summary>The default URL is the image's own literal, not a guess: 0x14705d6b4.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v2/orderforms/payment-page",
            RetailApiFamilies.JohnLewisBff.PaymentPageV2);
    }
}
