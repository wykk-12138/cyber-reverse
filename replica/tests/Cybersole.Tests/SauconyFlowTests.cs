using System.Linq;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1309: Saucony, the store the catalogue was missing.
///
/// <para>
/// The interesting assertions are the refusals. A flow that fetches a home page and a product page and
/// then declines the rest <em>by name</em> is a different claim from one that pretends to check out, and
/// these cases pin the difference: each undecoded step must name its own state-machine ordinal, so a
/// reader lands on the right function in the image instead of on a generic failure.
/// </para>
/// </summary>
public sealed class SauconyFlowTests
{
    [Fact]
    public void TheCatalogueCarriesTheStoreAndItsDomain()
    {
        var modules = Cybersole.Stores.Modules.StoreModuleCatalog.CreateAll();

        var module = Assert.Single(modules.Where(m => m.Id == "saucony"));
        Assert.Equal("Saucony", module.Name);
        Assert.Contains("saucony.com", module.Domains);
    }

    [Fact]
    public void TheFourStoreIdsAreTheOnesInTheImage()
    {
        Assert.Equal(new[] { "saucony_us", "saucony_ca", "saucony_eu", "saucony_europe" },
            SauconyFlow.StoreIds);
    }

    [Theory]
    [InlineData("https://www.saucony.com/collections/all", "saucony_us")]
    [InlineData("https://saucony.ca/products/x", "saucony_ca")]
    [InlineData("https://www.saucony.co.uk/products/x", "saucony_eu")]
    [InlineData("https://saucony.eu/products/x", "saucony_europe")]
    [InlineData("https://example.com/x", null)]
    [InlineData("", null)]
    public void TheStoreIdFollowsTheHost(string url, string? expected)
    {
        Assert.Equal(expected, SauconyFlow.StoreIdFor(url));
    }

    [Fact]
    public async Task TheHomeStepFetchesAndTheProductStepReportsWhatItFound()
    {
        using var server = new TinyServer((req, _) =>
            (req.RawUrl ?? string.Empty).Contains("/product", System.StringComparison.Ordinal)
                ? (200, "{\"name\":\"Endorphin Elite\",\"price\":\"225.00\"}")
                : (200, "<html>saucony</html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };

        var flow = new SauconyFlow();

        var home = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        Assert.True((await flow.GetHomeAsync(home, default)).Ok);

        var product = new FlowContext { Http = http, Url = server.BaseUrl + "/product/1" };
        Assert.True((await flow.FindProductAsync(product, default)).Ok);
        Assert.Equal("Endorphin Elite", product.Session.Vars["product"]);
        Assert.Equal("225.00", product.Session.Vars["price"]);
    }

    [Fact]
    public async Task FullSfccUsCheckoutWalksAllStepsEndToEnd()
    {
        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/on/demandware.store/Sites-saucony_us-Site/default/ProductInfo-GetDimensionsAndVariations")
            {
                return (200, """
                    {
                      "error": false,
                      "productName": "Endorphin Pro 4",
                      "price": { "sales": { "value": 225.00 } },
                      "color": { "values": [ { "value": "BLK", "displayValue": "Black", "selected": true } ] },
                      "variations": [
                        { "id": "S20939-10-95", "size": "9.5", "available": true },
                        { "id": "S20939-10-100", "size": "10", "available": true }
                      ]
                    }
                    """);
            }

            if (path == "/on/demandware.store/Sites-saucony_us-Site/default/Cart-AddProduct")
            {
                return (200, """
                    <div class="mini-cart-total">
                      <span class="mini-cart-quantity-bag">1</span>
                      <a class="mini-cart-name">Endorphin Pro 4</a>
                      <img src="/images/endorphin.jpg" />
                    </div>
                    """);
            }

            if (path == "/en/checkout")
                return (200, """<script>window.app = { csrfToken: "csrf_saucony_1" };</script>""");

            if (path == "/on/demandware.store/Sites-saucony_us-Site/default/Checkout-ContinueToBilling")
                return (200, """{"isShippingDataProvided":true}""");

            if (path == "/on/demandware.store/Sites-saucony_us-Site/default/Checkout-SubmitPaymentDetails")
                return (200, """{"error":false,"cart":{"valid":{"error":false}}}""");

            if (path == "/on/demandware.store/Sites-saucony_us-Site/default/CheckoutHelper-PlaceOrder")
                return (200, """{"error":false,"redirectUrl":"/confirmation?orderNo=SAU-8801"}""");

            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var flow = new SauconyFlow();
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/p/endorphin-pro-4.html",
            Product = new Product { Input = "S20939-10", Sizes = new() { "10" }, Color = "Black" },
            ProfileData = new Profile
            {
                FirstName = "Ada", LastName = "Lovelace", Email = "ada@saucony.test", Phone = "5551234567",
                Address1 = "1 Main St", City = "Boston", State = "MA", Zip = "02110", Country = "US",
            },
            Card = new Card { Number = "4111111111111111", Month = "7", Year = "2030", Cvv = "737", Name = "Ada Lovelace" },
        };

        var fp = await flow.FindProductAsync(ctx, default);
        Assert.True(fp.Ok, fp.Error);
        Assert.Equal("S20939-10-100", ctx.Session.VariantId);
        Assert.Equal("BLK", ctx.Session.Vars["saucony.color"]);

        var atc = await flow.AddToCartAsync(ctx, default);
        Assert.True(atc.Ok, atc.Error);
        var atcReq = Assert.Single(server.Requests, r => r.Path.EndsWith("/Cart-AddProduct"));
        Assert.Contains("usertype=Wide", atcReq.Body);
        Assert.Contains("cartAction=add", atcReq.Body);
        Assert.Contains("masterpid=S20939-10", atcReq.Body);
        Assert.Contains("pid=S20939-10-100", atcReq.Body);

        var co = await flow.GetCheckoutAsync(ctx, default);
        Assert.True(co.Ok, co.Error);
        Assert.Equal("csrf_saucony_1", ctx.Session.Vars["csrfToken"]);

        var ship = await flow.SubmitShippingAsync(ctx, default);
        Assert.True(ship.Ok, ship.Error);
        var shipReq = Assert.Single(server.Requests, r => r.Path.EndsWith("/Checkout-ContinueToBilling"));
        Assert.Contains("dwfrm_singleshipping_shippingAddress_addressFields_states_state=MA", shipReq.Body);
        Assert.Contains("bypassBEV=true", shipReq.Body);
        Assert.Contains("csrf_token=csrf_saucony_1", shipReq.Body);

        var bill = await flow.SubmitBillingAsync(ctx, default);
        Assert.True(bill.Ok, bill.Error);
        var billReq = Assert.Single(server.Requests, r => r.Path.EndsWith("/Checkout-SubmitPaymentDetails"));
        Assert.Contains("dwfrm_billing_paymentMethods_creditCard_type=Visa", billReq.Body);
        Assert.Contains("dwfrm_billing_paymentMethods_creditCard_expiration=07%2F2030", billReq.Body);
        Assert.Contains("dwfrm_billing_billingAddress_addressFields_states_state=MA", billReq.Body);

        var order = await flow.SubmitOrderAsync(ctx, default);
        Assert.True(order.Ok, order.Error);
        Assert.Equal("SAU-8801", ctx.Session.OrderNumber);
    }

    [Fact]
    public async Task EuPayerAuthenticateAndHandleOrderResultBranchesMatchSfccContract()
    {
        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/UK/en_GB/checkout")
                return (200, """<script>csrfToken: "csrf_uk_1",</script>""");

            if (path == "/on/demandware.store/Sites-saucony_eu-Site/en_GB/CheckoutHelper-PlaceOrder")
            {
                if (body.Contains("isPayerValidationCall=true"))
                    return (200, """{"stepUpUrl":"https://centinelapi.cardinalcommerce.com/V2/Cruise/StepUp","jwt":"val_jwt_1","MD":"md_uk_1"}""");
                if (body.Contains("isPayerAuthenticCall=true"))
                    return (200, """{"error":false,"orderNo":"SAU-UK-42"}""");
                return (200, """{"isPAEnable":true,"jwtToken":"init_jwt_1"}""");
            }

            if (path == "/cardinal/stepup")
                return (200, "<html>ok</html>");

            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var flow = new SauconyFlow();

        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/UK/en_GB/p/1",
            ProfileData = new Profile { Country = "GB" },
        };
        ctx.Session.Vars["saucony.siteName"] = "saucony_eu";
        ctx.Session.Vars["saucony.stepUpUrl"] = server.BaseUrl + "/cardinal/stepup";

        Assert.True((await flow.GetCheckoutAsync(ctx, default)).Ok);
        var order = await flow.SubmitOrderAsync(ctx, default);
        Assert.True(order.Ok, order.Error);
        Assert.Equal("init_jwt_1", ctx.Session.Vars["saucony.jwtToken"]);
        Assert.Equal("SAU-UK-42", ctx.Session.OrderNumber);

        var stepUpReq = Assert.Single(server.Requests, r => r.Path == "/cardinal/stepup");
        Assert.Contains("JWT=val_jwt_1", stepUpReq.Body);
        Assert.Contains("MD=md_uk_1", stepUpReq.Body);
        Assert.Contains("PayerAuth-Return", stepUpReq.Body);

        // HandleOrderResult branches: /cart redirect -> restock, declined -> non-retryable, errorMessage -> restock
        var cartRedirect = flow.HandleOrderResult(ctx, """{"redirectUrl":"/cart?err=1"}""");
        Assert.False(cartRedirect.Ok);
        Assert.True(cartRedirect.Retryable);
        Assert.Equal("Waiting for restock", cartRedirect.Error);

        var declined = flow.HandleOrderResult(ctx, """{"error":true,"paymentError":{"declined":true}}""");
        Assert.False(declined.Ok);
        Assert.False(declined.Retryable);
        Assert.Equal("Card declined", declined.Error);

        var restockMsg = flow.HandleOrderResult(ctx, """{"error":true,"errorMessage":"Your order could not be submitted."}""");
        Assert.False(restockMsg.Ok);
        Assert.True(restockMsg.Retryable);
        Assert.Equal("Waiting for restock", restockMsg.Error);
    }

    /// <summary>
    /// R1375: PayerAuthenticate used to refuse every call. It still cannot build the request, but it can read the
    /// reply — a redirect, a step-up, or the handler's own sentence.
    /// </summary>
    [Fact]
    public void ThePayerStepClassifiesInsteadOfRefusing()
    {
        var flow = new SauconyFlow();

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var bare = new FlowContext { Http = http, Url = "https://www.saucony.com/" };
        var withoutReply = flow.PayerAuthenticate(bare);
        Assert.False(withoutReply.Ok);
        Assert.Contains("d__13", withoutReply.Error);

        var context = new FlowContext { Http = http, Url = "https://www.saucony.com/" };
        context.Session.Vars["saucony.threeDsReply"] = "{\"redirectUrl\":\"https://acs.example/r\"}";
        var withRedirect = flow.PayerAuthenticate(context);

        Assert.True(withRedirect.Ok);
        Assert.Equal("Redirect", context.Session.Vars["saucony.threeDsShape"]);
        Assert.Equal("https://acs.example/r", context.Session.Vars["saucony.threeDsUrl"]);
    }

    /// <summary>A reply with neither url gets the handler's own words, not a generic failure.</summary>
    [Fact]
    public void AnUnexpectedReplyUsesTheHandlersSentence()
    {
        var flow = new SauconyFlow();
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var context = new FlowContext { Http = http, Url = "https://www.saucony.com/" };
        context.Session.Vars["saucony.threeDsReply"] = "{\"error\":\"declined\"}";

        var outcome = flow.PayerAuthenticate(context);

        Assert.False(outcome.Ok);
        Assert.Equal("Unexpected 3DS response", outcome.Error);
    }
}
