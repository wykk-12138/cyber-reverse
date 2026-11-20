using System.Collections.Generic;
using System.Web;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Pins the <c>Cybersole.Models.{State,Country,Address}</c> records from descriptor 0x143211f9d
/// and their live projection inside <see cref="DemandwareFlow.SubmitShippingAsync"/>.
/// </summary>
public sealed class AddressModelsTests
{
    [Fact]
    public void ModelsPreserveDescriptorFieldShapeWithoutCollidingWithCoreModels()
    {
        var state = new Cybersole.Models.State("California");
        var country = new Cybersole.Models.Country("United States", "US", new[] { state });
        var address = new Cybersole.Models.Address(
            "Ada", "Lovelace", "10 Downing St", "Apt 2", "San Jose", "95113",
            country, state, "Poblacion");

        Assert.Equal("California", address.State?.Name);
        Assert.Equal("US", address.Country?.Code);
        Assert.Single(address.Country!.States);
        Assert.Equal("Poblacion", address.Barangay);

        // Distinct from Cybersole.Core.Models.Address / Country used on FlowContext.
        var coreAddress = new Cybersole.Core.Models.Address
        {
            FirstName = "Ada",
            LastName = "Lovelace",
            State = "CA",
        };
        Assert.Equal("Ada Lovelace", coreAddress.FullName);
        Assert.NotEqual(typeof(Cybersole.Models.Address), typeof(Cybersole.Core.Models.Address));
    }

    [Fact]
    public async Task DemandwareSubmitShippingProjectsStateAndAddressFields()
    {
        string postedBody = string.Empty;
        string requestedUrl = string.Empty;
        using var server = new TinyServer((req, body) =>
        {
            requestedUrl = req.RawUrl ?? string.Empty;
            postedBody = body ?? string.Empty;
            return (200, "{\"ok\":true}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/shop/product",
            Shipping = new Cybersole.Core.Models.Address
            {
                FirstName = "Grace",
                LastName = "Hopper",
                Address1 = "1700 Navy Way",
                City = "Arlington",
                State = "VA",
                ZipCode = "22202",
                Country = "US",
            },
        };
        ctx.Session.CsrfToken = "csrf-tok-42";

        var flow = new DemandwareFlow("dw", "Demandware", new[] { "shop.example" }, "Shop", "en_US");
        var outcome = await flow.SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok);
        Assert.Contains("CheckoutShippingServices-SubmitShipping", requestedUrl);

        var form = HttpUtility.ParseQueryString(postedBody);
        Assert.Equal("Grace", form["dwfrm_shipping_shippingAddress_addressFields_firstName"]);
        Assert.Equal("Hopper", form["dwfrm_shipping_shippingAddress_addressFields_lastName"]);
        Assert.Equal("1700 Navy Way", form["dwfrm_shipping_shippingAddress_addressFields_address1"]);
        Assert.Equal("Arlington", form["dwfrm_shipping_shippingAddress_addressFields_city"]);
        Assert.Equal("VA", form["dwfrm_shipping_shippingAddress_addressFields_states_stateCode"]);
        Assert.Equal("22202", form["dwfrm_shipping_shippingAddress_addressFields_postalCode"]);
        Assert.Equal("US", form["dwfrm_shipping_shippingAddress_addressFields_country"]);
        Assert.Equal("csrf-tok-42", form["csrf_token"]);
    }
}
