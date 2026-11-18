using System.Linq;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1087: the decoded Stripe gateway contract — the method-create form from the shared state
/// machine (sub_140bda320), the PopMart desk pair beside it, and the desk chain the gateway's
/// AuthorizeAsync drives.
/// </summary>
public sealed class StripeMethodFormTests
{
    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://www.popmart.com/order/123/order/?payType=stripe",
        Shipping = new Address { Country = "GB" },
        Card = new Card { Number = "4242424242424242", Month = "12", Year = "2030", Cvv = "737" },
    };

    /// <summary>
    /// The decoded form — every key, the frozen values verbatim, the card fields from context,
    /// and the radar slot the challenge's hCaptcha token rides.
    /// </summary>
    [Fact]
    public void TheMethodCreateFormMatchesTheDecodedContract()
    {
        var ctx = Context(null!);
        ctx.Session.Vars["stripe.publishableKey"] = "pk_test_popmart";

        var f = StripeGateway.MethodCreateForm(ctx, "hc-token-9", "cs-1", "g-1", "m-1", "s-1");

        Assert.Equal(22, f.Count);
        Assert.Equal(new[]
        {
            "billing_details[address][country]", "type", "card[number]", "card[cvc]",
            "card[exp_year]", "card[exp_month]", "allow_redisplay", "payment_user_agent",
            "referrer", "time_on_page", "radar_options[hcaptcha_token]",
            "client_attribution_metadata[client_session_id]",
            "client_attribution_metadata[merchant_integration_source]",
            "client_attribution_metadata[merchant_integration_subtype]",
            "client_attribution_metadata[merchant_integration_version]",
            "client_attribution_metadata[payment_intent_creation_flow]",
            "client_attribution_metadata[payment_method_selection_flow]",
            "guid", "muid", "sid", "key", "_stripe_version",
        }, f.Keys.ToArray());

        // Context-sourced values.
        Assert.Equal("GB", f["billing_details[address][country]"]);
        Assert.Equal("4242424242424242", f["card[number]"]);
        Assert.Equal("737", f["card[cvc]"]);
        Assert.Equal("2030", f["card[exp_year]"]);
        Assert.Equal("12", f["card[exp_month]"]);
        Assert.Equal("pk_test_popmart", f["key"]);
        Assert.Equal("hc-token-9", f["radar_options[hcaptcha_token]"]);

        // The frozen fingerprint, verbatim — the image's own literals.
        Assert.Equal("card", f["type"]);
        Assert.Equal("unspecified", f["allow_redisplay"]);
        Assert.Equal(StripeGateway.PaymentUserAgent, f["payment_user_agent"]);
        Assert.Equal("https://www.popmart.com", f["referrer"]);
        Assert.Equal(StripeGateway.TimeOnPage, f["time_on_page"]);
        Assert.Equal("elements", f["client_attribution_metadata[merchant_integration_source]"]);
        Assert.Equal("payment-element", f["client_attribution_metadata[merchant_integration_subtype]"]);
        Assert.Equal("2021", f["client_attribution_metadata[merchant_integration_version]"]);
        Assert.Equal("deferred", f["client_attribution_metadata[payment_intent_creation_flow]"]);
        Assert.Equal("automatic", f["client_attribution_metadata[payment_method_selection_flow]"]);
        Assert.Equal(StripeGateway.FormVersion, f["_stripe_version"]);
        Assert.Equal("2025-01-27.acacia", f["_stripe_version"]);   // this form's frozen version
    }

    /// <summary>
    /// The desk pair and the machine's order: session (orderNum) → method create → desk pay
    /// (orderNum / paymentMethodId / setupFutureUsage / returnURL composed the machine's own way).
    /// </summary>
    [Fact]
    public async Task TheDeskChainRunsInMachineOrder()
    {
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            bodies.Add((req.Url?.AbsolutePath ?? "") + " " + body);
            if (req.Url?.AbsolutePath.Contains("customerSession") == true)
                return (200, "{\"publishableKey\":\"pk_live_desk\"}");
            if (req.Url?.AbsolutePath.EndsWith("/v1/payment_methods") == true)
                return (200, "{\"id\":\"pm_77\"}");
            if (req.Url?.AbsolutePath.EndsWith("desk/stripe/pay") == true)
                return (200, "{\"status\":\"PAID\"}");
            return (404, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.CartId = "ord-909";
        ctx.Session.Vars["stripe.deskHost"] = server.BaseUrl;
        ctx.Session.Vars["stripe.apiUrl"] = server.BaseUrl;   // the v1 seam, same convention

        var result = await new StripeGateway().AuthorizeAsync(ctx, default);

        Assert.True(result.Ok, result.Error);

        // Machine order: customerSession first (its answer supplies the publishable key),
        // then the v1 method create, then the desk pay.
        Assert.Equal(3, bodies.Count);
        Assert.Contains("desk/stripe/customerSession", bodies[0]);
        Assert.Contains("orderNum=ord-909", bodies[0]);
        Assert.Contains("/v1/payment_methods", bodies[1]);
        Assert.Contains("radar_options%5Bhcaptcha_token%5D=", bodies[1]);   // the radar slot went out
        Assert.Contains("desk/stripe/pay", bodies[2]);

        // The publishable key the session read supplied the create.
        Assert.Contains("pk_live_desk", bodies[1]);

        // The desk pay form: the decoded four keys, the return URL composed the machine's way.
        Assert.Contains("orderNum=ord-909", bodies[2]);
        Assert.Contains("paymentMethodId=pm_77", bodies[2]);
        Assert.Contains("setupFutureUsage=", bodies[2]);
        Assert.Contains(
            "returnURL=" + System.Uri.EscapeDataString(
                server.BaseUrl + "/ord-909/order/?payType=stripe"),
            bodies[2]);

        Assert.Equal("pm_77", ctx.Session.PaymentMethodId);
    }

    /// <summary>The desk paths and the two frozen API versions are the image's own.</summary>
    [Fact]
    public void TheDeskPathsAndVersionsMatchTheFrozenLiterals()
    {
        Assert.Equal("/shop/v1/shop/cash/desk/stripe/customerSession", StripeGateway.DeskCustomerSessionPath);
        Assert.Equal("/shop/v1/shop/cash/desk/stripe/pay", StripeGateway.DeskPayPath);
        Assert.Equal("2025-01-27.acacia", StripeGateway.FormVersion);
        // The challenge surface's constant is the image's other frozen version — pinned where
        // it lives, in PAYMENT_CHALLENGES's probe set; here the pair's existence is asserted by
        // this form carrying acacia, not basil.
        Assert.DoesNotContain("basil", StripeGateway.FormVersion);
    }
}
