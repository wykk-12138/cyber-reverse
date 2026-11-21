using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1358: Braintree's client token. The handler names the request field and the reply key, and gives the failure
/// its own words — a run should read the same here as in the image.
/// </summary>
public sealed class BraintreeClientTokenTests
{
    [Fact]
    public void TheDocumentAndTheHandlersFieldNames()
    {
        Assert.Equal("generateClientToken", BraintreeClientToken.OperationName);
        Assert.Equal(188, BraintreeClientToken.Document.Length);
        Assert.StartsWith("query generateClientToken($type: String)", BraintreeClientToken.Document);
        Assert.Equal("authorizationFingerprint", BraintreeClientToken.AuthorizationFingerprintField);
        Assert.Equal("clientToken", BraintreeClientToken.ClientTokenField);
        Assert.Equal("Error getting token", BraintreeClientToken.ErrorGettingTokenMessage);
    }

    [Fact]
    public async Task WithoutAnEndpointNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (token, error) = await BraintreeClientToken.FetchAsync(ctx, null, new JObject(), default);

        Assert.Null(token);
        Assert.Contains("no endpoint", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheReplyCarriesTheToken()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"clientToken\":\"eyJ0eXAi\"}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (token, error) = await BraintreeClientToken.FetchAsync(
            ctx, server.BaseUrl + "/graphql", new JObject { ["type"] = "paypal" }, default);

        Assert.Equal("eyJ0eXAi", token);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("generateClientToken", sent["operationName"]!.ToObject<string>());
        Assert.Equal(BraintreeClientToken.Document, sent["query"]!.ToObject<string>());
        Assert.Equal("paypal", sent["variables"]!["type"]!.ToObject<string>());
    }

    /// <summary>A reply without a token becomes the handler's message, not a raw failure.</summary>
    [Fact]
    public async Task AReplyWithoutATokenUsesTheHandlersWords()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (token, error) = await BraintreeClientToken.FetchAsync(
            ctx, server.BaseUrl + "/graphql", new JObject(), default);

        Assert.Null(token);
        Assert.Equal(BraintreeClientToken.ErrorGettingTokenMessage, error);
    }

    /// <summary>The session step reaches it, so the class is not an island.</summary>
    [Fact]
    public async Task TheSessionStepFetchesTheToken()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"clientToken\":\"tok-1\"}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["braintree.endpoint"] = server.BaseUrl + "/graphql";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.GetSessionAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("tok-1", ctx.Session.Vars["clientToken"]);
    }
}
