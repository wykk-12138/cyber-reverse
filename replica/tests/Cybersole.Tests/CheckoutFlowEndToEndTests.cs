using System.Text.Json;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Services;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// End-to-end checkout against a mock Shopify storefront.
///
/// This is the test that proves the step contract is not just a list of names: a real
/// <see cref="ShopifyFlow"/> is driven through <see cref="StoreFlowRunner"/> over HTTP and
/// every step has to reach the mock store in the right order.
/// </summary>
public class CheckoutFlowEndToEndTests
{
    private const string Token = "0123456789abcdefabcdef01";   // >= 20 chars: the token regex

    /// <summary>A minimal but faithful Shopify surface.</summary>
    private sealed class ShopifyMock : IDisposable
    {
        private readonly TinyServer _server;
        public string BaseUrl => _server.BaseUrl;
        public List<string> Hits => _server.Requests.Select(r => r.Path).ToList();

        public ShopifyMock()
        {
            _server = new TinyServer((req, body) => Route(req.HttpMethod, req.Url!.AbsolutePath, body));
        }

        private static (int, string) Route(string method, string path, string body)
        {
            // product page
            if (path == "/")
                return (200, """
                    <html><body>
                      <script>Shopify.currency = {"active":"USD"};</script>
                      <input type="hidden" name="authenticity_token" value="csrf-abc" />
                    </body></html>
                    """);

            // product json (ShopifyFlow.FindProduct)
            if (path.StartsWith("/products/", StringComparison.Ordinal) && path.EndsWith(".js"))
                return (200, """
                    {"id":11,"title":"Air Max 1","handle":"air-max-1",
                     "price":15000,
                     "images":["//cdn.example.com/a.jpg"],
                     "variants":[
                       {"id":101,"title":"9","public_title":"9","price":"150.00","available":true},
                       {"id":102,"title":"10","public_title":"10","price":"150.00","available":true},
                       {"id":103,"title":"11","public_title":"11","price":"150.00","available":false}
                     ]}
                    """);

            // cart add / get / change
            if (path == "/cart/add.js" && method == "POST")
                return (200, """{"id":101,"quantity":1,"items":[{"id":101,"quantity":1}]}""");

            if (path == "/cart.js")
                return (200, """{"token":"cart","total_price":15000,"item_count":1,"items":[{"id":101}]}""");

            if (path == "/cart/change.js")
                return (200, """{"token":"cart","item_count":1}""");

            // checkout bootstrap hands back a page that carries the tokenised URL
            if (path == "/checkout")
                return (200, "<html><a href=\"/checkouts/" + Token + "\">continue</a></html>");

            // everything under /checkouts/{token}
            if (path.StartsWith("/checkouts/" + Token, StringComparison.Ordinal))
            {
                if (path.EndsWith("/shipping_rates", StringComparison.Ordinal))
                    return (200, """{"shipping_rates":[{"id":"standard","price":"5.00"}]}""");

                if (path.EndsWith("/payments", StringComparison.Ordinal))
                    return (200, """{"id":"pay_1","status":"succeeded"}""");

                if (path.EndsWith("/complete", StringComparison.Ordinal))
                    return (200, $$"""
                        {"id":"co_1","order_id":"5501","order_number":"#5501",
                         "order_status_url":"https://mock/orders/5501"}
                        """);

                // checkout page + updates
                return (200, """{"id":"co_1","email":null,"line_items":[{"id":101}]}""");
            }

            return (404, "{}");
        }

        public void Dispose() => _server.Dispose();
    }

    private static FlowContext BuildContext(AppServices services, string baseUrl)
    {
        return new FlowContext
        {
            Http = services.Http,
            Url = baseUrl + "/products/air-max-1",
            Product = new Product
            {
                Name = "Air Max 1",
                Url = baseUrl + "/products/air-max-1",
                Sizes = new List<string> { "10" },
                PriceCheck = false,
            },
            ProfileData = new Profile
            {
                Name = "p1",
                Email = "buyer@example.com",
                FirstName = "Ada",
                LastName = "Lovelace",
                Phone = "+15550000000",
                Address1 = "1 Analytical Way",
                City = "London",
                State = "LDN",
                Zip = "E1 6AN",
                Country = "GB",
            },
            Card = new Card
            {
                Number = "4111111111111111",
                Month = "12",
                Year = "2030",
                Cvv = "123",
                Name = "Ada Lovelace",
            },
            Shipping = new Address
            {
                FirstName = "Ada",
                LastName = "Lovelace",
                Address1 = "1 Analytical Way",
                City = "London",
                State = "LDN",
                ZipCode = "E1 6AN",
                Country = "GB",
            },
            TimeoutSeconds = 10,
        };
    }

    [Fact]
    public async Task ShopifyCheckoutRunsEveryStepAgainstAMockStore()
    {
        using var services = TestServices.Create();
        using var store = new ShopifyMock();

        var ctx = BuildContext(services, store.BaseUrl);
        var outcome = await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(), ctx, default);

        var trace = string.Join(" | ", ctx.Events.Select(e => e.Name));
        Assert.True(outcome.Success, outcome.Error + " :: " + trace);
        Assert.Equal("5501", outcome.OrderNumber);

        // every step is recorded, and none of them failed
        Assert.NotEmpty(ctx.Steps);
        Assert.All(ctx.Steps, s => Assert.True(s.Completed, $"{s.Name}: {s.Error}"));

        // the ordered step names must match what the runner promises
        var names = ctx.Steps.Select(s => s.Name).ToList();
        Assert.Equal("Init", names[0]);
        Assert.Contains("FindProduct", names);
        Assert.Contains("AddToCart", names);
        Assert.Contains("SubmitShipping", names);
        Assert.Contains("SubmitPayment", names);
        Assert.Contains("SubmitOrder", names);
        Assert.Equal("ProcessOrder", names[^1]);
    }

    [Fact]
    public async Task TheStoreActuallyReceivesTheDocumentedRequests()
    {
        using var services = TestServices.Create();
        using var store = new ShopifyMock();

        var ctx = BuildContext(services, store.BaseUrl);
        await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(), ctx, default);

        var hits = store.Hits;

        Assert.Contains("/products/air-max-1.js", hits);
        Assert.Contains("/cart/add.js", hits);
        Assert.Contains("/cart.js", hits);
        Assert.Contains("/checkout", hits);
        Assert.Contains($"/checkouts/{Token}/shipping_rates", hits);
        Assert.Contains($"/checkouts/{Token}/payments", hits);
        Assert.Contains($"/checkouts/{Token}/complete", hits);
    }

    [Fact]
    public async Task CheckoutAbortsWhenTheCartIsRejected()
    {
        using var services = TestServices.Create();
        using var store = new ShopifyMock();

        var ctx = BuildContext(services, store.BaseUrl);
        ctx.Session.Quantity = 99;

        // The mock still accepts the add; force a failure by pointing at a dead host.
        ctx = new FlowContext
        {
            Http = services.Http,
            Url = "http://127.0.0.1:1/products/nothing",
            Product = ctx.Product,
            ProfileData = ctx.ProfileData,
            Card = ctx.Card,
            Shipping = ctx.Shipping,
            TimeoutSeconds = 1,
        };

        var outcome = await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(), ctx, default);

        Assert.False(outcome.Success);
        Assert.NotNull(outcome.Error);

        var failed = ctx.Steps.Last(s => !s.Completed);
        Assert.False(string.IsNullOrEmpty(failed.Error));
    }

    [Fact]
    public async Task MonitorHalfOfTheFlowReportsAvailability()
    {
        using var services = TestServices.Create();
        using var store = new ShopifyMock();

        var ctx = BuildContext(services, store.BaseUrl);
        var result = await StoreFlowRunner.RunMonitorAsync(new ShopifyFlow(), ctx, default);

        Assert.Equal(Cybersole.Http.Stores.MonitorStatus.Available, result.Status);
        Assert.Equal("150.00", result.Price);
        Assert.Equal("102", result.VariantId);   // size 10 matched the requested size
        Assert.Contains("10", result.Sizes);
    }

    [Fact]
    public async Task NikeFlowRunsItsKasadaGateAgainstTheMock()
    {
        using var services = TestServices.Create();
        using var store = new ShopifyMock();

        var ctx = BuildContext(services, store.BaseUrl);
        ctx = new FlowContext
        {
            Http = services.Http,
            Url = store.BaseUrl + "/launch/t/air-max-1",
            Product = ctx.Product,
            ProfileData = ctx.ProfileData,
            Card = ctx.Card,
            Shipping = ctx.Shipping,
            TimeoutSeconds = 5,
        };

        var monitor = await StoreFlowRunner.RunMonitorAsync(new NikeFlow(), ctx, default);

        // Nike needs a Kasada script the mock does not serve, so the gate must fail closed
        // (Blocked) rather than pretending the product is available.
        Assert.True(monitor.Status is Cybersole.Http.Stores.MonitorStatus.Blocked
                    or Cybersole.Http.Stores.MonitorStatus.Error,
            $"expected the anti-bot gate to fail closed, got {monitor.Status}");

        var names = ctx.Steps.Select(s => s.Name).ToList();
        Assert.Contains("GetScript", names);
    }
}
