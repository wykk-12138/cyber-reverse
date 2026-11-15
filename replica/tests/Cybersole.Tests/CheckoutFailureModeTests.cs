using Cybersole.Core.Models;
using Cybersole.Http.Stores;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Failure-mode coverage for the step runner: a store that answers 403 / 429 / 422 must be
/// classified correctly instead of collapsing into a generic error.
/// </summary>
public class CheckoutFailureModeTests
{
    private static FlowContext Ctx(Cybersole.Services.AppServices services, string baseUrl) => new()
    {
        Http = services.Http,
        Url = baseUrl + "/products/x",
        Product = new Product
        {
            Name = "x",
            Url = baseUrl + "/products/x",
            Sizes = new List<string> { "10" },
        },
        ProfileData = new Profile
        {
            Email = "a@b.c",
            FirstName = "A",
            LastName = "B",
            Address1 = "1 St",
            City = "C",
            State = "S",
            Zip = "1",
            Country = "US",
        },
        Card = new Card { Number = "4111111111111111", Month = "12", Year = "30", Cvv = "123" },
        TimeoutSeconds = 5,
    };

    [Fact]
    public async Task ForbiddenHomeIsReportedAsACaptchaWall()
    {
        using var services = TestServices.Create();
        using var store = new TinyServer(_ => (403, "blocked"));

        var result = await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(),
            Ctx(services, store.BaseUrl), default);

        Assert.Equal(MonitorStatus.Captcha, result.Status);
    }

    [Fact]
    public async Task RateLimitedHomeIsReportedAsBlocked()
    {
        using var services = TestServices.Create();
        using var store = new TinyServer(_ => (429, "slow down"));

        var result = await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(),
            Ctx(services, store.BaseUrl), default);

        Assert.Equal(MonitorStatus.Blocked, result.Status);
    }

    [Fact]
    public async Task ServerErrorStaysAGenericError()
    {
        using var services = TestServices.Create();
        using var store = new TinyServer(_ => (503, "down"));

        var result = await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(),
            Ctx(services, store.BaseUrl), default);

        Assert.Equal(MonitorStatus.Error, result.Status);
    }

    [Fact]
    public async Task UnreachableHostFailsCleanly()
    {
        using var services = TestServices.Create();
        var ctx = Ctx(services, "http://127.0.0.1:1");
        ctx = new FlowContext
        {
            Http = services.Http,
            Url = "http://127.0.0.1:1/products/x",
            Product = ctx.Product,
            ProfileData = ctx.ProfileData,
            Card = ctx.Card,
            TimeoutSeconds = 1,
        };

        var result = await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(), ctx, default);
        Assert.NotEqual(MonitorStatus.Available, result.Status);
        Assert.False(string.IsNullOrEmpty(result.Error));
    }

    [Fact]
    public async Task UnprocessableCartIsADeclineNotAnError()
    {
        using var services = TestServices.Create();

        // home + product succeed, cart/add returns 422
        using var store = new TinyServer((req, _) =>
        {
            var path = req.Url!.AbsolutePath;

            if (path == "/") return (200, "<html></html>");
            if (path.EndsWith(".js", StringComparison.Ordinal) && path.StartsWith("/products/"))
                return (200, """
                    {"title":"x","variants":[{"id":1,"title":"10","public_title":"10","price":"10.00","available":true}]}
                    """);
            if (path == "/cart/add.js") return (422, """{"description":"sold out"}""");
            return (404, "{}");
        });

        var outcome = await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(),
            Ctx(services, store.BaseUrl), default);

        Assert.False(outcome.Success);
        Assert.Equal(CheckoutResult.Declined, outcome.Result);
    }

    [Fact]
    public async Task ConflictDuringCheckoutIsAlsoADecline()
    {
        using var services = TestServices.Create();

        using var store = new TinyServer((req, _) =>
        {
            var path = req.Url!.AbsolutePath;

            if (path == "/") return (200, "<html></html>");
            if (path.EndsWith(".js", StringComparison.Ordinal) && path.StartsWith("/products/"))
                return (200, """
                    {"title":"x","variants":[{"id":1,"title":"10","public_title":"10","price":"10.00","available":true}]}
                    """);
            if (path == "/cart/add.js") return (409, "{}");
            return (404, "{}");
        });

        var outcome = await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(),
            Ctx(services, store.BaseUrl), default);

        Assert.False(outcome.Success);
        Assert.Equal(CheckoutResult.Declined, outcome.Result);
    }

    [Fact]
    public async Task TheLastStatusIsRecordedOnTheSession()
    {
        using var services = TestServices.Create();
        using var store = new TinyServer(_ => (403, "no"));

        var ctx = Ctx(services, store.BaseUrl);
        await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(), ctx, default);

        Assert.Equal("403", ctx.Session.Vars["lastStatus"]);
        Assert.Contains(store.BaseUrl, ctx.Session.Vars["lastUrl"]);
    }
}
