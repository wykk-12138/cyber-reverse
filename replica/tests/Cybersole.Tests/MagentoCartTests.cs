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
}
