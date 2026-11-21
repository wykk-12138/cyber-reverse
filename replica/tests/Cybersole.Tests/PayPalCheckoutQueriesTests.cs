using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1343: PayWithQuery and ShipToQuery, both sent by sub_14110D030 to the partner base — the same base the
/// approval and the currency conversion use.
/// </summary>
public sealed class PayPalCheckoutQueriesTests
{
    [Fact]
    public void BothEndpointsShareThePartnerBase()
    {
        Assert.Equal(PayPalPartnerApprove.BaseUrl, PayPalCheckoutQueries.BaseUrl);
        Assert.Equal("https://www.paypal.com/graphql/PayWithQuery", PayPalCheckoutQueries.PayWithUrl);
        Assert.Equal("https://www.paypal.com/graphql/ShipToQuery", PayPalCheckoutQueries.ShipToUrl);
        Assert.NotEqual(PayPalCheckoutQueries.PayWithUrl, PayPalCheckoutQueries.ShipToUrl);
    }

    [Fact]
    public void TheDocumentsAreTheStringsTheImageHolds()
    {
        Assert.Equal(12561, PayPalCheckoutQueries.PayWithDocument.Length);
        Assert.StartsWith("query PayWithQuery($token: String!", PayPalCheckoutQueries.PayWithDocument);
        Assert.Equal(2031, PayPalCheckoutQueries.ShipToDocument.Length);
        Assert.StartsWith("query ShipToQuery($token: String!)", PayPalCheckoutQueries.ShipToDocument);
    }

    /// <summary>
    /// The sender writes "expeirences" while the document declares $experiences — the same split the currency
    /// sender has. Correcting it would send a different request, so the pairing is pinned here.
    /// </summary>
    [Fact]
    public void TheVariableKeyKeepsTheImagesSpelling()
    {
        Assert.Equal(new[] { "token", "withSplitTender", "expeirences" },
            PayPalCheckoutQueries.PayWithVariableNames);
        Assert.Contains("$experiences", PayPalCheckoutQueries.PayWithDocument);
        Assert.DoesNotContain("$expeirences", PayPalCheckoutQueries.PayWithDocument);
        Assert.Contains("$withSplitTender", PayPalCheckoutQueries.PayWithDocument);
        Assert.Contains("$token", PayPalCheckoutQueries.ShipToDocument);
    }

    [Fact]
    public async Task ATokenlessQueryIsRefusedBeforeAnyRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (session, error) = await PayPalCheckoutQueries.PayWithAsync(ctx, new JObject(), default);

        Assert.Null(session);
        Assert.Contains("no token", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task ThePayWithQueryPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"checkoutSession\":{\"token\":\"t-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (session, error) = await PayPalCheckoutQueries.PayWithAsync(
            ctx,
            new JObject { ["token"] = "t-1", ["withSplitTender"] = false, ["expeirences"] = new JArray() },
            default, server.BaseUrl + "/graphql/PayWithQuery");

        Assert.NotNull(session);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("PayWithQuery", sent["operationName"]!.ToObject<string>());
        Assert.Equal(PayPalCheckoutQueries.PayWithDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("t-1", sent["variables"]!["token"]!.ToObject<string>());
        Assert.False(sent["variables"]!["withSplitTender"]!.ToObject<bool>());
    }

    [Fact]
    public async Task TheShipToQueryUsesItsOwnDocument()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"checkoutSession\":{\"merc\":\"m\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (session, error) = await PayPalCheckoutQueries.ShipToAsync(
            ctx, new JObject { ["token"] = "t-2" }, default, server.BaseUrl + "/graphql/ShipToQuery");

        Assert.NotNull(session);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("ShipToQuery", sent["operationName"]!.ToObject<string>());
        Assert.Equal(PayPalCheckoutQueries.ShipToDocument, sent["query"]!.ToObject<string>());
    }
}
