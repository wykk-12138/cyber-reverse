using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1357: a family that identifies its queries by hash instead of sending them. The mechanism is observed; which
/// hash belongs to which operation is not, so a hash is always the caller's to supply.
/// </summary>
public sealed class GraphQlHashQueriesTests
{
    [Fact]
    public void TheHeaderNamesAreTheObservedOnes()
    {
        Assert.Equal("x-graphql-hash", GraphQlHashQueries.HashHeader);
        Assert.Equal("x-graphql-query-name", GraphQlHashQueries.QueryNameHeader);
        Assert.Equal("x-header-id", GraphQlHashQueries.HeaderIdHeader);
    }

    [Fact]
    public void TwoHashesAreObservedAndNeitherIsAssigned()
    {
        Assert.Equal(2, GraphQlHashQueries.ObservedHashes.Length);
        foreach (var hash in GraphQlHashQueries.ObservedHashes)
        {
            Assert.Equal(64, hash.Length);
            Assert.Matches("^[0-9a-f]{64}$", hash);
        }
        Assert.NotEqual(GraphQlHashQueries.ObservedHashes[0], GraphQlHashQueries.ObservedHashes[1]);
    }

    [Fact]
    public void TheThreeDocumentsAreTheMeasuredOnes()
    {
        Assert.Equal(74, GraphQlHashQueries.GetCartCookieDocument.Length);
        Assert.StartsWith("query GetCartCookie {", GraphQlHashQueries.GetCartCookieDocument);
        Assert.Equal(490, GraphQlHashQueries.GetProductInventoryDocument.Length);
        Assert.Equal(3520, GraphQlHashQueries.GetCartDocument.Length);
        Assert.StartsWith("query GetCart {", GraphQlHashQueries.GetCartDocument);
    }

    /// <summary>With a hash the query travels as a header; without one the document goes in the body.</summary>
    [Fact]
    public void TheEnvelopeDropsTheDocumentOnlyWhenAHashIsGiven()
    {
        var withDocument = GraphQlHashQueries.Envelope("GetCartCookie", new JObject(), includeDocument: true);
        var byHash = GraphQlHashQueries.Envelope("GetCartCookie", new JObject(), includeDocument: false);

        Assert.NotNull(withDocument["query"]);
        Assert.Null(byHash["query"]);
        Assert.Equal("GetCartCookie", byHash["operationName"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, null, "GetCart", new JObject(), null, default);

        Assert.Null(data);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task WithAHashTheBodyCarriesNoQuery()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"getCart\":{\"id\":\"c-1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, server.BaseUrl, "GetCart", new JObject(), "a".PadRight(64, '0'), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Null(sent["query"]);
        Assert.Equal("GetCart", sent["operationName"]!.ToObject<string>());
    }

    /// <summary>Without a hash the same call still sends a valid request, in the long form.</summary>
    [Fact]
    public async Task WithoutAHashTheDocumentIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"getCart\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, server.BaseUrl, "GetCart", new JObject(), null, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(GraphQlHashQueries.GetCartDocument, sent["query"]!.ToObject<string>());
    }

    /// <summary>
    /// R1364: updateShipAddress' handler carries x-graphql-hash and two more 64-hex values, so it joins the family
    /// that identifies its queries by hash. Its document declares one variable.
    /// </summary>
    [Fact]
    public void TheShipAddressJoinsTheHashFamily()
    {
        Assert.Equal(140, GraphQlHashQueries.UpdateShipAddressDocument.Length);
        Assert.StartsWith("mutation updateShipAddress($address: AddressInput!)",
            GraphQlHashQueries.UpdateShipAddressDocument);
        Assert.Same(GraphQlHashQueries.UpdateShipAddressDocument,
            GraphQlHashQueries.DocumentFor("updateShipAddress"));
    }

    /// <summary>Without a hash the family still sends a well-formed request.</summary>
    [Fact]
    public async Task TheShipAddressSendsItsDocumentWhenNoHashIsGiven()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"updateShipAddress\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/graphql" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "updateShipAddress",
            new JObject { ["address"] = new JObject() }, null, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(GraphQlHashQueries.UpdateShipAddressDocument, sent["query"]!.ToObject<string>());
    }
}
