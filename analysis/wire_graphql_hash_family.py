"""Wire the hash family into the cart step, and test the mechanism."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/GraphQlHashQueriesTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'GraphQlHashQueries' not in text:
    # The cart step's virtual: process the cart. Anchor on its declaration only.
    marker = 'public virtual Task<StepOutcome> ProcessCartAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('no cart step virtual to hang the branch on')

    # Replace the NotSupported body with a branch that consults the hash family.
    body_end = text.find(';', position)
    original = text[position:body_end + 1]
    replacement = '''public virtual async Task<StepOutcome> ProcessCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1357: the family that posts persisted queries by hash. When a run names an origin for it, the cart is
        // read through it; the hash comes from the run because the image holds two and pairs neither with an
        // operation.
        var origin = c.Session.Vars.GetValueOrDefault("graphqlHash.origin");
        if (!string.IsNullOrEmpty(origin))
        {
            var (data, error) = await GraphQlHashQueries.SendAsync(c, origin, "GetCart", new Newtonsoft.Json.Linq.JObject(),
                c.Session.Vars.GetValueOrDefault("graphqlHash.cartHash"), ct).ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(error);

            c.Session.Vars["cart"] = data.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return await NotSupported("ProcessCart").ConfigureAwait(false);
    }'''
    text = text[:position] + replacement + text[body_end + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('cart step now consults the hash family')

tests = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1357: a family that identifies its queries by hash instead of sending them. The mechanism is what is observed;
/// which hash belongs to which operation is not, so the hash is always the caller's.
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
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"getCart\\":{\\"id\\":\\"c-1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, server.BaseUrl, "GetCart", new JObject(), "a".PadRight(64, '0'), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Null(sent["query"]);
        Assert.Equal(server.Requests[0].Body!.Contains("GetCart"), true);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
