using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1338: Highsnobiety, built from the two senders R1337 read — host, operation names, envelope and variable
/// names are observed; the value of $action is not, and is refused rather than guessed.
/// </summary>
public sealed class HighsnobietyFlowTests
{
    [Fact]
    public void TheStoreIsIdentifiedByItsCustomerDomainAndItsApiIsSeparate()
    {
        var flow = new HighsnobietyFlow();

        Assert.Equal("highsnobiety", flow.Id);
        Assert.Equal("Highsnobiety", flow.Name);
        Assert.Contains("highsnobiety.com", flow.Domains);
        Assert.Equal("https://tm-api-eu.highsnobiety.com/", HighsnobietyFlow.ApiHost);
        Assert.DoesNotContain("tm-api-eu.highsnobiety.com", flow.Domains);
    }

    [Fact]
    public void BothDocumentsAreTheImageStrings()
    {
        Assert.Equal(3435, HighsnobietyFlow.AddLineItemDocument.Length);
        Assert.StartsWith("mutation addLineItem($country: Country!, $action: AddCartLineItem!",
            HighsnobietyFlow.AddLineItemDocument);
        Assert.Equal(3399, HighsnobietyFlow.AddDiscountCodeDocument.Length);
        Assert.StartsWith("mutation addDiscountCode($code: String!", HighsnobietyFlow.AddDiscountCodeDocument);
    }

    [Fact]
    public void TheVariableNamesAreTheDocumentsOwn()
    {
        Assert.Equal(new[] { "action", "country", "locale" }, HighsnobietyFlow.AddLineItemVariables);
        foreach (var name in HighsnobietyFlow.AddLineItemVariables)
            Assert.Contains("$" + name, HighsnobietyFlow.AddLineItemDocument);
    }

    /// <summary>
    /// $action is typed as an enum in the document and the image never names a member, so a run without it is
    /// told what to set. Guessing would send a request whose meaning nobody can check.
    /// </summary>
    [Fact]
    public async Task WithoutTheActionTheStepSaysWhatToSet()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().AddToCartAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("highsnobiety.action", outcome.Error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheAddPostsTheObservedEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"addLineItem\":{\"id\":\"line-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.action"] = "{\"sku\":\"HS-1\",\"quantity\":1}";
        ctx.Session.Vars["highsnobiety.country"] = "DE";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().AddToCartAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("addLineItem", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.AddLineItemDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("HS-1", sent["variables"]!["action"]!["sku"]!.ToObject<string>());
        Assert.Equal(1, sent["variables"]!["action"]!["quantity"]!.ToObject<int>());
        Assert.Null(sent["variables"]!["sku"]);
        Assert.Equal("DE", sent["variables"]!["country"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["locale"]!.ToObject<string>());
    }

    [Fact]
    public async Task TheDiscountPostsItsOwnOperationName()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().AddDiscountCodeAsync(ctx, "SAVE10", default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("addDiscountCode", sent["operationName"]!.ToObject<string>());
        Assert.Equal("SAVE10", sent["variables"]!["code"]!.ToObject<string>());
    }

    /// <summary>
    /// R1338: the document carries CRLF, and a text-editor pass over this file silently turned them into LF —
    /// 206 characters vanished from a verbatim string with nothing to catch it. The literal now spells \r\n
    /// out, and this pins the count so the next pass fails loudly instead of quietly.
    /// </summary>
    [Fact]
    public void TheDocumentKeepsItsLineEndings()
    {
        Assert.Equal(206, CountOf(HighsnobietyFlow.AddLineItemDocument, "\r\n"));
        Assert.DoesNotContain("\n", HighsnobietyFlow.AddLineItemDocument.Replace("\r\n", ""));
        Assert.Equal(206, CountOf(HighsnobietyFlow.AddDiscountCodeDocument, "\r\n"));
    }

    private static int CountOf(string text, string needle)
    {
        var count = 0;
        var index = text.IndexOf(needle, System.StringComparison.Ordinal);
        while (index >= 0)
        {
            count++;
            index = text.IndexOf(needle, index + needle.Length, System.StringComparison.Ordinal);
        }

        return count;
    }

    /// <summary>
    /// R1339: the product query's document declares five variables, and the step fills all five — the slug from
    /// the run, the three locale fields defaulting to each other, and the country from the profile.
    /// </summary>
    [Fact]
    public async Task TheProductQueryCarriesAllFiveVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"product\":{\"id\":\"p-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            ProfileData = new Cybersole.Core.Models.Profile { Country = "DE" },
        };
        ctx.Session.Vars["slug"] = "hs-tee";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("fetchProduct", sent["operationName"]!.ToObject<string>());
        Assert.Equal(5718, HighsnobietyFlow.FetchProductDocument.Length);
        Assert.Equal(HighsnobietyFlow.FetchProductDocument, sent["query"]!.ToObject<string>());
        var variables = sent["variables"]!;
        Assert.Equal("hs-tee", variables["slug"]!.ToObject<string>());
        Assert.Equal("de", variables["country"]!.ToObject<string>().ToLowerInvariant());
        Assert.Equal("en", variables["locale"]!.ToObject<string>());
        Assert.Equal("en", variables["preferredLocale"]!.ToObject<string>());
        Assert.Equal("en", variables["fallbackLocale"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutASlugTheProductQueryIsNotSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().FindProductAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// The email mutation's own input type is SetCartCustomerEmail, not the cart line's AddCartLineItem — the two
    /// are per-operation objects, which is why each step has its own session key.
    /// </summary>
    [Fact]
    public async Task TheEmailStepSendsItsOwnActionObject()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.emailAction"] = "{\"email\":\"ada@example.test\"}";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitEmailAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(4986, HighsnobietyFlow.SetCustomerEmailDocument.Length);
        Assert.StartsWith("mutation setCustomerEmail($action: SetCartCustomerEmail!", HighsnobietyFlow.SetCustomerEmailDocument);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("setCustomerEmail", sent["operationName"]!.ToObject<string>());
        Assert.Equal("ada@example.test", sent["variables"]!["action"]!["email"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutTheEmailActionNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitEmailAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("highsnobiety.emailAction", outcome.Error);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// R1341: the confirmation query is keyed by the Stripe payment-intent id. Its document is 4825 characters at
    /// 0x14713E1FC and the sender at 0x140B574F0 passes exactly these three variables.
    /// </summary>
    [Fact]
    public async Task TheOrderStepConfirmsWithThePaymentIntent()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"order\":{\"number\":\"HS-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["stripePaymentIntentId"] = "pi_123";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitOrderAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(4825, HighsnobietyFlow.FetchOrderConfirmationDocument.Length);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("fetchOrderConfirmation", sent["operationName"]!.ToObject<string>());
        Assert.Equal("pi_123", sent["variables"]!["stripePaymentIntentId"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["locale"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["preferredLocale"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutAPaymentIntentTheOrderStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("stripePaymentIntentId", outcome.Error);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// R1350: the payment mutation, 222 characters, placed by its sender's address (0x140B56EA4, inside this
    /// store's own payment sender) rather than by its signature — which matched no family the cluster script knew.
    /// </summary>
    [Fact]
    public void ThePaymentStepCarriesItsTwoVariables()
    {
        Assert.Equal(222, HighsnobietyFlow.CreateCheckoutPaymentDocument.Length);
        Assert.StartsWith("mutation createCheckoutPayment($storefront: Storefront", 
            HighsnobietyFlow.CreateCheckoutPaymentDocument);
        Assert.Contains("$withoutShippingAddressSet", HighsnobietyFlow.CreateCheckoutPaymentDocument);
    }

    [Fact]
    public async Task WithoutAStorefrontThePaymentStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("$storefront", outcome.Error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task ThePaymentStepPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"createCheckoutPayment\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.storefront"] = "hs-store";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("createCheckoutPayment", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.CreateCheckoutPaymentDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("hs-store", sent["variables"]!["storefront"]!.ToObject<string>());
        Assert.False(sent["variables"]!["withoutShippingAddressSet"]!.ToObject<bool>());
    }

    /// <summary>
    /// R1354: shipping is the store's third address step. Its document is 4992 characters and declares the same
    /// shape as billing and email — one action object plus two locales — which is what placed it here, together
    /// with its sender being the function the host sweep had already labelled as shipping.
    /// </summary>
    [Fact]
    public void TheShippingStepIsTheThirdAddressStep()
    {
        Assert.Equal(4992, HighsnobietyFlow.SetShippingAddressDocument.Length);
        Assert.StartsWith("mutation setShippingAddress($action: SetCartShippingAddress!",
            HighsnobietyFlow.SetShippingAddressDocument);
        Assert.Contains("$locale", HighsnobietyFlow.SetShippingAddressDocument);
        Assert.Contains("$preferredLocale", HighsnobietyFlow.SetShippingAddressDocument);

        // The three address-shaped documents share the action-plus-two-locales signature, and no two are equal.
        Assert.NotEqual(HighsnobietyFlow.SetBillingAddressDocument, HighsnobietyFlow.SetShippingAddressDocument);
        Assert.NotEqual(HighsnobietyFlow.SetCustomerEmailDocument, HighsnobietyFlow.SetShippingAddressDocument);
    }

    [Fact]
    public async Task WithoutAShippingActionTheStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitShippingAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheShippingStepPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"setShippingAddress\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";
        ctx.Session.Vars["highsnobiety.shippingAction"] =
            "{\"type\":\"SetCartShippingAddress\",\"address\":{\"city\":\"Seoul\"}}";

        var outcome = await new HighsnobietyFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("setShippingAddress", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.SetShippingAddressDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("Seoul",
            sent["variables"]!["action"]!["address"]!["city"]!.ToObject<string>());
    }
}
