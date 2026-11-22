using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1320: Magento's cart documents, read out of the image byte for byte.
///
/// <para>
/// The three documents are pinned exactly — 240, 32 and 61 characters — because they are the finding: the
/// add mutation carries <c>%CART_ID%</c>, <c>%QTY%</c> and <c>%SKU%</c> as literal substitution tokens rather
/// than using GraphQL variables, and a helper that quietly converted them to variables would be a different
/// request from the one the image sends.
/// </para>
/// </summary>
public sealed class MagentoCartTests
{
    [Fact]
    public void TheDocumentsAreTheStringsTheImageHolds()
    {
        Assert.Equal(240, MagentoCart.AddProductsDocument.Length);
        Assert.Equal(32, MagentoCart.CreateEmptyCartDocument.Length);
        Assert.Equal(61, MagentoCart.CustomerCartDocument.Length);

        Assert.StartsWith("mutation {\r\n  addProductsToCart(cartId: \"%CART_ID%\"", MagentoCart.AddProductsDocument);
        Assert.EndsWith("user_errors { code message }\r\n  }\r\n}", MagentoCart.AddProductsDocument);
        Assert.Equal("mutation {\n    createEmptyCart\n}", MagentoCart.CreateEmptyCartDocument);
        Assert.Equal("{ customerCart { id total_quantity items { uid quantity } } }", MagentoCart.CustomerCartDocument);
    }

    [Fact]
    public void TheTokensAreTheThreeTheDocumentSubstitutes()
    {
        Assert.Equal(new[] { "%CART_ID%", "%QTY%", "%SKU%" }, MagentoCart.Placeholders);
        foreach (var token in MagentoCart.Placeholders)
            Assert.Contains(token, MagentoCart.AddProductsDocument);
    }

    [Fact]
    public void FillingReplacesEveryTokenAndLeavesNone()
    {
        var document = MagentoCart.FillAddProducts("abc123", "GA-2100-1A", 2);

        Assert.DoesNotContain("%CART_ID%", document);
        Assert.DoesNotContain("%QTY%", document);
        Assert.DoesNotContain("%SKU%", document);
        Assert.Contains("cartId: \"abc123\"", document);
        Assert.Contains("quantity: 2,", document);
        Assert.Contains("sku: \"GA-2100-1A\"", document);
        // Same length as the template plus the difference between the tokens and their values.
        Assert.Equal(MagentoCart.AddProductsDocument.Length
                     - "%CART_ID%".Length - "%QTY%".Length - "%SKU%".Length
                     + "abc123".Length + "2".Length + "GA-2100-1A".Length, document.Length);
    }

    [Fact]
    public void ASkuWithAQuoteCannotBreakTheDocument()
    {
        var document = MagentoCart.FillAddProducts("cart", "weird\"sku", 1);

        Assert.Contains("sku: \"weird\\\"sku\"", document);
    }

    [Fact]
    public void AnEmptyCartIdIsRefusedBeforeAnyRequest()
    {
        Assert.Throws<System.ArgumentException>(() => MagentoCart.FillAddProducts("", "sku", 1));
    }

    [Fact]
    public async Task ACreatedCartIsReadBackOutOfTheReply()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"createEmptyCart\":\"masked-1\"}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var cartId = await MagentoCart.CreateEmptyAsync(ctx, server.BaseUrl + "/graphql", default);

        Assert.Equal("masked-1", cartId);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.CreateEmptyCartDocument, sent["query"]!.Value<string>());
    }

    /// <summary>
    /// Magento answers 200 and puts a rejected line in <c>user_errors</c>, so a caller that only checked the
    /// HTTP status would call a failed add a success. This is the case that pins the difference.
    /// </summary>
    [Fact]
    public async Task AUserErrorIsAFailureEvenThoughTheStatusIsTwoHundred()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"addProductsToCart\":{\"cart\":null,\"user_errors\":[{\"code\":\"OUT_OF_STOCK\",\"message\":\"not enough\"}]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var result = await MagentoCart.AddProductAsync(ctx, server.BaseUrl + "/graphql", "masked-1", "SKU1", 1, default);

        Assert.False(result.Ok);
        Assert.Contains("not enough", result.Error);
    }

    [Fact]
    public async Task ASuccessfulAddReportsTheCartTotals()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"addProductsToCart\":{\"cart\":{\"id\":\"masked-1\",\"total_quantity\":3," +
                 "\"items\":[{\"id\":\"9\",\"quantity\":3}],\"prices\":{\"grand_total\":{\"value\":297.5,\"currency\":\"USD\"}}}," +
                 "\"user_errors\":[]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var result = await MagentoCart.AddProductAsync(ctx, server.BaseUrl + "/graphql", "masked-1", "SKU1", 3, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("masked-1", result.CartId);
        Assert.Equal("3", result.TotalQuantity);
        Assert.Equal("297.5", result.GrandTotal);
        Assert.Equal("USD", result.Currency);
        Assert.Contains("sku: \"SKU1\"", JObject.Parse(server.Requests[0].Body!)["query"]!.Value<string>());
    }

    /// <summary>
    /// R1321: the billing document, 323 characters from 0x1470E4F94 — Magento's updateMyCart with two actions.
    /// It uses GraphQL variables, unlike the add mutation's substitution tokens, so the two documents in this
    /// class are filled in two different ways and both have to stay that way.
    /// </summary>
    [Fact]
    public void TheBillingDocumentIsTheStringTheImageHolds()
    {
        Assert.Equal(323, MagentoCart.AddBillingAddressDocument.Length);
        Assert.StartsWith("mutation addBillingAddressToCart($cartId: String!, $version: Long!, " +
                          "$address: AddressInput!, $emailAddress: String)", MagentoCart.AddBillingAddressDocument);
        Assert.Contains("{setBillingAddress: {address: $address}}, {setCustomerEmail: {email: $emailAddress}}",
            MagentoCart.AddBillingAddressDocument);
        Assert.EndsWith("    id\n    version\n    isAbleToCheckout\n  }\n}", MagentoCart.AddBillingAddressDocument);
    }

    [Fact]
    public async Task TheBillingStepSendsVariablesAndKeepsTheNewVersion()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"updateMyCart\":{\"id\":\"masked-9\",\"version\":7,\"isAbleToCheckout\":true}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.sku"] = "GA-2100-1A";
        ctx.Session.Vars["casio.cartId"] = "masked-9";
        ctx.Session.Vars["casio.cartVersion"] = "6";
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";
        ctx.Session.Vars["email"] = "buyer@example.test";

        var outcome = await new CasioFlow().SubmitBillingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("7", ctx.Session.Vars["casio.cartVersion"]);
        Assert.Equal("true", ctx.Session.Vars["casio.isAbleToCheckout"]);

        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.AddBillingAddressDocument, sent["query"]!.Value<string>());
        Assert.Equal("masked-9", sent["variables"]!["cartId"]!.ToString());
        Assert.Equal(6, sent["variables"]!["version"]!.Value<long>());
        Assert.Equal("buyer@example.test", sent["variables"]!["emailAddress"]!.ToString());
    }

    /// <summary>
    /// The version is a required variable the add mutation never returns, so the step refuses rather than
    /// inventing one. A fabricated 0 or 1 would be a number the store validates and rejects.
    /// </summary>
    [Fact]
    public async Task WithoutAVersionTheBillingStepSaysWhichVariableIsMissing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.cartId"] = "masked-9";
        ctx.Session.Vars["email"] = "buyer@example.test";

        var outcome = await new CasioFlow().SubmitBillingAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("cart version", outcome.Error);
        Assert.Empty(server.Requests);
    }
    [Fact]
    public async Task TheCasioStepCreatesACartThenAddsTheLine()
    {
        using var server = new TinyServer((req, body) =>
        {
            var target = req.RawUrl ?? string.Empty;
            if (target.Contains("/graphql", System.StringComparison.Ordinal))
            {
                if (body.Contains("createEmptyCart", System.StringComparison.Ordinal))
                    return (200, "{\"data\":{\"createEmptyCart\":\"masked-9\"}}");
                return (200, "{\"data\":{\"addProductsToCart\":{\"cart\":{\"id\":\"masked-9\",\"total_quantity\":1," +
                            "\"items\":[],\"prices\":{\"grand_total\":{\"value\":99,\"currency\":\"USD\"}}},\"user_errors\":[]}}}");
            }
            return (500, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.sku"] = "GA-2100-1A";
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().AddToCartAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("masked-9", ctx.Session.Vars["casio.cartId"]);
        Assert.Equal("1", ctx.Session.Vars["casio.cartTotal"]);
        Assert.Equal(2, server.Requests.Count);
        Assert.False(ctx.Session.Vars.ContainsKey("casio.cartGraphQlError"));
    }

    /// <summary>
    /// R1322: the payment and order documents, 236 and 141 characters. addPaymentToCart is the third member
    /// of the updateMyCart family, and SubmitOrder takes a cart token — not the cart id — which is why the
    /// order step refuses instead of posting whatever id it has.
    /// </summary>
    [Fact]
    public void ThePaymentAndOrderDocumentsAreTheStringsTheImageHolds()
    {
        Assert.Equal(236, MagentoCart.AddPaymentDocument.Length);
        Assert.Contains("updateMyCart(", MagentoCart.AddPaymentDocument);
        Assert.Contains("actions: {addPayment: {payment: {id: $paymentId}}}", MagentoCart.AddPaymentDocument);

        Assert.Equal(141, MagentoCart.SubmitOrderDocument.Length);
        Assert.Contains("submitOrder(cartToken: $cartToken)", MagentoCart.SubmitOrderDocument);
        Assert.EndsWith("    id\n    customerId\n    orderNumber\n    __typename\n  }\n}", MagentoCart.SubmitOrderDocument);
    }

    [Fact]
    public async Task APaymentIsAttachedWithTheVersionTheCartIsAt()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"updateMyCart\":{\"id\":\"masked-9\",\"version\":8,\"isAbleToCheckout\":true}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var result = await MagentoCart.AddPaymentAsync(ctx, server.BaseUrl + "/graphql", "masked-9", 7, "pay-1", default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("8", result.Version);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("pay-1", sent["variables"]!["paymentId"]!.ToString());
        Assert.Equal(7, sent["variables"]!["version"]!.Value<long>());
    }

    [Fact]
    public async Task AnOrderNumberIsReadOutOfTheSubmission()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"submitOrder\":{\"id\":\"o-1\",\"customerId\":\"c-1\",\"orderNumber\":\"CS-1000342\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var result = await MagentoCart.SubmitOrderAsync(ctx, server.BaseUrl + "/graphql", "token-1", default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("CS-1000342", result.OrderNumber);
        Assert.Equal("c-1", result.CustomerId);
    }

    /// <summary>
    /// A submission that answers no order number is a failure, not a success with an empty field: the order
    /// number is the only thing that says an order exists.
    /// </summary>
    [Fact]
    public async Task ASubmissionWithoutAnOrderNumberIsAFailure()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"submitOrder\":{\"id\":\"o-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var result = await MagentoCart.SubmitOrderAsync(ctx, server.BaseUrl + "/graphql", "token-1", default);

        Assert.False(result.Ok);
        Assert.Contains("no order number", result.Error);
    }

    [Fact]
    public async Task TheOrderStepUsesTheCartTokenWhenThereIsOne()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"submitOrder\":{\"id\":\"o-1\",\"customerId\":\"c-1\",\"orderNumber\":\"CS-9\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.cartToken"] = "token-1";
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().SubmitOrderAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("CS-9", ctx.Session.OrderNumber);
        Assert.Equal("o-1", ctx.Session.Vars["casio.orderId"]);
    }

    /// <summary>
    /// Without a token the step keeps the Unzer route's own refusal — and that refusal is unchanged, which is
    /// the point of putting the token branch beside it rather than replacing it.
    /// </summary>
    [Fact]
    public async Task WithoutATokenTheUnzerRefusalStands()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://casio.test/products/x" };

        var outcome = await new CasioFlow().SubmitOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("unzer_cards", outcome.Error);
    }

    /// <summary>
    /// R1329: CustomerCartDocument was declared in R1320 and had no caller — a document the replica could not
    /// send. The step reads the cart through it, and this pins the query that goes out.
    /// </summary>
    [Fact]
    public async Task TheCartReadUsesTheImageQuery()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"customerCart\":{\"id\":\"masked-9\",\"total_quantity\":2," +
                 "\"items\":[{\"uid\":\"a\",\"quantity\":2}]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().GetCartAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("masked-9", ctx.Session.Vars["cart"]);
        Assert.Equal("2", ctx.Session.Vars["casio.cartTotal"]);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.CustomerCartDocument, sent["query"]!.Value<string>());
    }

    /// <summary>
    /// A store that keys carts by masked id answers no customerCart. That is a failure to report, not an empty
    /// cart — the difference decides whether the run continues with a cart it does not have.
    /// </summary>
    [Fact]
    public async Task ACartReplyWithoutCustomerCartIsAFailure()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().GetCartAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("customerCart", outcome.Error);
        Assert.False(ctx.Session.Vars.ContainsKey("cart"));
    }

    /// <summary>
    /// R1369: getShippingMethods is Magento 2's shipping query — carrier_code/method_code with prices and an address
    /// argument in Magento's snake_case shape. It references twelve variables and declares none, which is how the
    /// image carries it; a replica that declared them would send a different request.
    /// </summary>
    [Fact]
    public void TheShippingMethodsQueryIsMagentos()
    {
        var document = MagentoCart.ShippingMethodsDocument;

        Assert.Equal(531, document.Length);
        Assert.StartsWith("query getShippingMethods {", document);
        foreach (var field in new[] { "carrier_code", "method_code", "carrier_title", "method_title",
                                      "price_excl_tax", "price_incl_tax", "save_in_address_book" })
            Assert.Contains(field, document);
        Assert.Contains("$region", document);
        Assert.DoesNotContain("$region:", document);
    }

    /// <summary>No endpoint, no request — the store's own host is never guessed.</summary>
    [Fact]
    public async Task TheShippingQueryNeedsTheStoresEndpoint()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await MagentoCart.GetShippingMethodsAsync(ctx, null, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no endpoint", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheShippingQueryPostsItsDocument()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"getShippingMethods\":[]}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await MagentoCart.GetShippingMethodsAsync(
            ctx, server.BaseUrl + "/graphql", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(MagentoCart.ShippingMethodsDocument, sent["query"]!.ToObject<string>());
    }

    /// <summary>
    /// R1377: addToCart and buynow carry Magento's vocabulary — sku/qty/quote_id/"Simple" — so they belong with this
    /// platform's documents rather than with the session family they were first filed under.
    /// </summary>
    [Fact]
    public void TheCartAndBuyNowDocumentsAreMagentos()
    {
        Assert.Contains("$sku", MagentoCart.AddToCartDocument);
        Assert.Contains("$qty", MagentoCart.AddToCartDocument);
        Assert.Contains("$type", MagentoCart.AddToCartDocument);

        Assert.StartsWith("query buynow", MagentoCart.BuyNowDocument);
        Assert.Contains("quote_id", MagentoCart.BuyNowDocument);
        Assert.Contains("isNormalBuyFlow", MagentoCart.BuyNowDocument);
        Assert.Contains("cart_id", MagentoCart.BuyNowDocument);
    }
}
