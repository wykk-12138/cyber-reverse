using System.Collections.Generic;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1136: the image has two delivery step names and two delivery endpoints — one carrying an address
/// and one carrying nothing — so each name gets one endpoint instead of both sharing the body-less one.
///
/// <c>SubmitShipping</c> (ordinal 27) now PUTs the address to <c>v4/orderforms/deliveries/delivery-address</c>
/// with the eleven-key, three-level body read off <c>sub_140A43A80</c>; <c>CreateDelivery</c>
/// (ordinal 28) keeps the body-less PUT to <c>v4/orderforms/deliveries</c>. The <b>assignment</b> of
/// names to endpoints is an inference from that 1:1 shape and the two names, not request capture.
/// </summary>
public sealed class JohnLewisDeliveryStepTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext
        {
            Http = http,
            Url = "https://www.johnlewis.com/ourshop/product",
            Shipping = new Address
            {
                FirstName = "Ada",
                LastName = "Lovelace",
                Address1 = "1 Oxford Street",
                City = "London",
                ZipCode = "W1D 1AN",
                Country = "GB",
            },
        };
        c.Session.Vars["jl.deliveryAddressUrl"] =
            server.BaseUrl + "/bff/v4/orderforms/deliveries/delivery-address";
        c.Session.Vars["jl.deliveriesUrl"] = server.BaseUrl + "/bff/v4/orderforms/deliveries";
        c.Session.Vars["jl.phoneNumber"] = "0207000000";
        return c;
    }

    [Fact]
    public async Task SubmitShippingPutsTheThreeLevelAddressBody()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " " + body);
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v4/orderforms/deliveries/delivery-address", request);

        // the whole nested body, not just the key names
        Assert.Contains("\"addressDetails\":{", request);
        Assert.Contains("\"addressee\":{\"firstName\":\"Ada\",\"lastName\":\"Lovelace\"}", request);
        Assert.Contains(
            "\"address\":{\"addressLine1\":\"1 Oxford Street\",\"townOrCity\":\"London\"," +
            "\"postcode\":\"W1D 1AN\",\"countryCode\":\"GB\"}",
            request);
        Assert.Contains("\"contact\":{\"phoneNumber\":\"0207000000\"}", request);
    }

    [Fact]
    public async Task CreateDeliveryKeepsTheBodylessConfirm()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod + " [" + body + "]");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().CreateDeliveryAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("PUT", request.Split(' ')[1]);
        Assert.Contains("/bff/v4/orderforms/deliveries", request);
        Assert.DoesNotContain("delivery-address", request);
        Assert.EndsWith("[]", request);   // no body at all
    }

    [Fact]
    public async Task NoShippingAddressStopsSubmitShipping()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://www.johnlewis.com/p/1" };

        var outcome = await new JohnLewisFlow().SubmitShippingAsync(ctx, default);

        Assert.False(outcome.Ok);
    }

    [Fact]
    public void BothDeliveryStepNamesAreKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("SubmitShipping"));
        Assert.True(StepActionRunner.Knows("CreateDelivery"));
    }

    [Fact]
    public void TheTwoConstantsAreTheImagesOwnUrls()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/orderforms/deliveries/delivery-address",
            RetailApiFamilies.JohnLewisBff.DeliveryAddressV4);
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/orderforms/deliveries",
            RetailApiFamilies.JohnLewisBff.DeliveriesV4);
    }
}
