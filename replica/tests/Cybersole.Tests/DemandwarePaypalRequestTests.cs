using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1164: the two order lookups actually go out, on the controller path and with their query.
///
/// R1163 added the methods but pinned only the constants, which is exactly the gap R1153 was about — a
/// method nobody calls in a test is a method nobody has checked. These drive both against a real socket
/// and assert the composed request line, so the Sites-{site}-Site prefix, the controller name and the
/// query all have to be right at once.
/// </summary>
public sealed class DemandwarePaypalRequestTests
{
    private static DemandwareFlow Flow() => new(
        "dw", "Demandware", new[] { "shop.example" }, "Shop", "en_US");

    private static FlowContext Context(NetClient http, string baseUrl) => new()
    {
        Http = http,
        Url = baseUrl + "/ourshop/product",
    };

    [Fact]
    public async Task TheOrderIdLookupCarriesTheTokenOnTheControllerPath()
    {
        string raw = string.Empty;
        using var server = new TinyServer((req, _) =>
        {
            raw = req.RawUrl ?? string.Empty;
            return (200, "{\"orderId\":\"O-1\"}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);

        var outcome = await Flow().PaypalOrderIdAsync(ctx, "tok-1", default);

        Assert.True(outcome.Ok);
        Assert.Equal("/on/demandware.store/Sites-Shop-Site/en_US/Paypal-GetPaypalOrderId?csrf_token=tok-1",
            raw);
        Assert.Equal("{\"orderId\":\"O-1\"}", ctx.Session.Vars["paypal.orderId"]);
    }

    [Fact]
    public async Task TheOrderDetailsLookupCarriesTheIdOnTheControllerPath()
    {
        string raw = string.Empty;
        using var server = new TinyServer((req, _) =>
        {
            raw = req.RawUrl ?? string.Empty;
            return (200, "{\"details\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server.BaseUrl);

        var outcome = await Flow().PaypalOrderDetailsAsync(ctx, "O-9", default);

        Assert.True(outcome.Ok);
        Assert.Equal("/on/demandware.store/Sites-Shop-Site/en_US/Paypal-GetOrderDetails?orderId=O-9", raw);
        Assert.Equal("{\"details\":true}", ctx.Session.Vars["paypal.orderDetails"]);
    }

    [Fact]
    public async Task ThePurchaseUnitReadIsAGetOnItsController()
    {
        string raw = string.Empty;
        string method = string.Empty;
        using var server = new TinyServer((req, _) =>
        {
            raw = req.RawUrl ?? string.Empty;
            method = req.HttpMethod ?? string.Empty;
            return (200, "{\"unit\":1}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };

        var outcome = await Flow().PaypalPurchaseUnitAsync(Context(http, server.BaseUrl), default);

        Assert.True(outcome.Ok);
        Assert.Equal("GET", method);
        Assert.Equal("/on/demandware.store/Sites-Shop-Site/en_US/Paypal-GetPurchaseUnit", raw);
    }
}
