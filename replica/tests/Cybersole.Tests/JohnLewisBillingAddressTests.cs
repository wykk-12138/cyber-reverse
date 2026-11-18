using System.Collections.Generic;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1128: John Lewis's <c>SubmitBillingAddress</c> — a POST to the BFF's
/// <c>v1/orderforms/payments/billing-address</c>.
///
/// The shape is read off <c>sub_140A424B0</c>: <c>firstName</c>+<c>lastName</c> land under
/// <c>addressee</c>, <c>addressLine1</c>+<c>townOrCity</c>+<c>postcode</c>+<c>countryCode</c> land under
/// <c>address</c>, and <c>phoneNumber</c> sits on the root. These facts pin that nesting, the verb, the
/// path, and the base class's four session keys.
/// </summary>
public sealed class JohnLewisBillingAddressTests
{
    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://www.johnlewis.com/ourshop/product",
        Shipping = new Address
        {
            Address1 = "1 Oxford Street",
            City = "London",
            ZipCode = "W1D 1AN",
            Country = "GB",
        },
    };

    [Fact]
    public async Task TheBodyNestsAddresseeAndAddressAsTheMachineDoes()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " " + body);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["jl.billingAddressUrl"] =
            server.BaseUrl + "/bff/v1/orderforms/payments/billing-address";
        ctx.Session.Vars["jl.firstName"] = "Ada";
        ctx.Session.Vars["jl.lastName"] = "Lovelace";
        ctx.Session.Vars["jl.phoneNumber"] = "0207000000";

        var outcome = await new JohnLewisFlow().SubmitBillingAddressAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("POST", request.Split(' ')[1]);
        Assert.Contains("/bff/v1/orderforms/payments/billing-address", request);

        // nesting, not a flat object: addressee carries the names, address carries the street fields
        Assert.Contains("\"addressee\":{\"firstName\":\"Ada\",\"lastName\":\"Lovelace\"}", request);
        Assert.Contains("\"addressLine1\":\"1 Oxford Street\"", request);
        Assert.Contains("\"townOrCity\":\"London\"", request);
        Assert.Contains("\"postcode\":\"W1D 1AN\"", request);
        Assert.Contains("\"countryCode\":\"GB\"", request);
        Assert.Contains("\"phoneNumber\":\"0207000000\"", request);
    }

    [Fact]
    public async Task TheBaseSessionKeysAreStillRecorded()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["jl.billingAddressUrl"] =
            server.BaseUrl + "/bff/v1/orderforms/payments/billing-address";

        var outcome = await new JohnLewisFlow().SubmitBillingAddressAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("1 Oxford Street", ctx.Session.Vars["billing.address1"]);
        Assert.Equal("London", ctx.Session.Vars["billing.city"]);
        Assert.Equal("W1D 1AN", ctx.Session.Vars["billing.zip"]);
        Assert.Equal("GB", ctx.Session.Vars["billing.country"]);
    }

    [Fact]
    public async Task NoAddressStopsTheStep()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.johnlewis.com/p/1" };

        var outcome = await new JohnLewisFlow().SubmitBillingAddressAsync(ctx, default);

        Assert.False(outcome.Ok);
    }

    /// <summary>The default URL is the image's own literal: 0x14705d600.</summary>
    [Fact]
    public void TheBffConstantIsTheImagesOwnUrl()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v1/orderforms/payments/billing-address",
            RetailApiFamilies.JohnLewisBff.BillingAddressV1);
    }
}
