using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 97: the Shopify Storefront GraphQL surface, character for character from the image.
///
/// <para>
/// The replica had no GraphQL path at all. The image carries:
/// </para>
///
/// <code>
/// api/2020-04/graphql.json   api/2021-10/graphql.json
/// api/2024-10/graphql.json   api/2025-04/graphql.json
/// /checkouts/internal/graphql
/// gid://shopify/SellingPlan…            (a selling-plan variant id)
/// -StorefrontToken                      (the tail of the token header)
/// </code>
///
/// <para>
/// plus two complete documents — a 354-character cart selection set and a 346-character
/// <c>cartLinesUpdate</c> mutation. Those are asserted here verbatim: if someone "tidies" the
/// query (reorders fields, drops a bracket) the test fails, because a changed selection set is a
/// changed request.
/// </para>
/// </summary>
public sealed class ShopifyGraphQlTests
{
    private readonly ITestOutputHelper _out;

    public ShopifyGraphQlTests(ITestOutputHelper output) => _out = output;

    /// <summary>The fragment is 354 characters, the mutation 346 — the image's own lengths.</summary>
    [Fact]
    public void TheDocumentsHaveTheImagesLengths()
    {
        _out.WriteLine($"selection: {ShopifyGraphQl.CartSelection.Length}");
        _out.WriteLine($"mutation:  {ShopifyGraphQl.CartLinesUpdate.Length}");

        Assert.Equal(354, ShopifyGraphQl.CartSelection.Length);
        Assert.Equal(346, ShopifyGraphQl.CartLinesUpdate.Length);
    }

    /// <summary>
    /// Brace accounting. The mutation is a whole document so its braces balance (12/12). The
    /// selection set is a <b>fragment</b>: the pool stores it starting at <c>"){id,checkoutUrl…"</c>
    /// — the <c>)</c> closes the <c>cart(…)</c> call, the selection set opens, and the document's own
    /// closing brace is included while its opening brace is not. So 12 open / 13 close is correct,
    /// and asserting equality here would force someone to "fix" a faithful copy.
    /// </summary>
    [Fact]
    public void TheDocumentBracesAreAccountedFor()
    {
        var selectionOpen = ShopifyGraphQl.CartSelection.Count(c => c == '{');
        var selectionClose = ShopifyGraphQl.CartSelection.Count(c => c == '}');
        var mutationOpen = ShopifyGraphQl.CartLinesUpdate.Count(c => c == '{');
        var mutationClose = ShopifyGraphQl.CartLinesUpdate.Count(c => c == '}');

        _out.WriteLine($"selection: {selectionOpen}/{selectionClose}  mutation: {mutationOpen}/{mutationClose}");

        Assert.Equal(12, selectionOpen);
        Assert.Equal(13, selectionClose);       // +1: the fragment drops the operation's opening brace
        Assert.Equal(mutationOpen, mutationClose);

        // the fragment really starts where the pool says it does
        Assert.StartsWith("\"){id,checkoutUrl", ShopifyGraphQl.CartSelection);
    }

    /// <summary>The fields a cart read has to return are all in the fragment.</summary>
    [Fact]
    public void TheSelectionCarriesEveryFieldTheFlowNeeds()
    {
        foreach (var field in new[]
                 {
                     "checkoutUrl", "totalQuantity", "subtotalAmount", "lines(first:250)",
                     "quantityAvailable", "availableForSale", "product{id,title,handle}",
                 })
        {
            Assert.Contains(field, ShopifyGraphQl.CartSelection);
        }

        Assert.Contains("cartLinesUpdate(cartId: $cartId, lines: $lines)", ShopifyGraphQl.CartLinesUpdate);
    }

    /// <summary>Four API versions, and the endpoint shape.</summary>
    [Fact]
    public void TheEndpointUsesTheImagesApiVersions()
    {
        Assert.Equal(4, ShopifyGraphQl.ApiVersions.Count);

        foreach (var version in ShopifyGraphQl.ApiVersions)
            _out.WriteLine(ShopifyGraphQl.Endpoint("shop.example.com", version));

        Assert.Equal("https://shop.example.com/api/2025-04/graphql.json",
            ShopifyGraphQl.Endpoint("shop.example.com"));
        Assert.Equal("https://shop.example.com/api/2020-04/graphql.json",
            ShopifyGraphQl.Endpoint("shop.example.com", "2020-04"));
        Assert.Equal("/checkouts/internal/graphql", ShopifyGraphQl.InternalCheckout);
    }

    /// <summary>The document assembly keeps the fragment verbatim after the query header.</summary>
    [Fact]
    public void TheDocumentAssemblyKeepsTheFragmentVerbatim()
    {
        var document = ShopifyGraphQl.CartQueryDocument("query Cart { cart(id: $cartId) ");

        Assert.StartsWith("query Cart { cart(id: $cartId) ", document);
        Assert.EndsWith(ShopifyGraphQl.CartSelection, document);
        Assert.Equal("query Cart { cart(id: $cartId) ".Length + 354, document.Length);
    }

    /// <summary>
    /// R98: the GraphQL read is wired into the flow, and the plain <c>/cart.js</c> read is still the
    /// fallback. A source-level check, because reaching either path needs a live storefront.
    ///
    /// <para>
    /// The interesting property is the <b>gate</b>: no storefront token means no GraphQL call. A
    /// storefront that does not offer a token is not an error, and the flow must not turn it into
    /// one — it just uses the endpoint it always used.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFlowGatesGraphQlOnATokenAndFallsBackToCartJs()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "ShopifyFlow.cs"));

        Assert.Contains("shopify.storefrontToken", source);
        Assert.Contains("shopify.cartId", source);
        Assert.Contains("GetCartViaGraphQlAsync", source);
        Assert.Contains("ShopifyGraphQl.CartQueryDocument", source);
        // R203: the header name moved into ShopifyHeaders; the flow references it by constant
        Assert.Contains("ShopifyHeaders.StorefrontAccessToken", source);
        Assert.Contains("X-Shopify-Storefront-Access-Token", ShopifyHeaders.StorefrontAccessToken);

        // the fallback is still there, and it is what runs when there is no token
        Assert.Contains("/cart.js", source);

        // GraphQL is inside an `if` on the token var, not unconditional
        var gate = source.IndexOf("TryGetValue(GraphQlTokenVar", StringComparison.Ordinal);
        var call = source.IndexOf("GetCartViaGraphQlAsync(c, token", StringComparison.Ordinal);
        _out.WriteLine($"gate at {gate}, call at {call}");

        Assert.True(gate > 0 && call > gate);
    }

    /// <summary><c>checkoutUrl</c> is found wherever the storefront nests it.</summary>
    [Fact]
    public void TheCheckoutUrlIsFoundAtAnyDepth()
    {
        const string direct = """
            {"data":{"cart":{"id":"gid://shopify/Cart/1","checkoutUrl":"https://shop.example.com/c/1","totalQuantity":1}}}
            """;
        const string nested = """
            {"data":{"cartLinesUpdate":{"cart":{"checkoutUrl":"https://shop.example.com/c/2"}}}}
            """;
        const string missing = """{"data":{"cart":{"id":"gid://shopify/Cart/1"}}}""";

        Assert.Equal("https://shop.example.com/c/1", ShopifyGraphQl.ParseCheckoutUrl(direct));
        Assert.Equal("https://shop.example.com/c/2", ShopifyGraphQl.ParseCheckoutUrl(nested));
        Assert.Null(ShopifyGraphQl.ParseCheckoutUrl(missing));
        Assert.Null(ShopifyGraphQl.ParseCheckoutUrl("not json"));
        Assert.Null(ShopifyGraphQl.ParseCheckoutUrl(null));
    }

    /// <summary>
    /// R1331: cartLinesUpdate had no caller since it was declared. With a cart id, a line id and a storefront
    /// token — all three of which the GraphQL cart read now supplies — the edit takes the structured path and
    /// sends the observed mutation.
    /// </summary>
    [Fact]
    public async Task TheLineEditTakesTheStructuredPath()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"cartLinesUpdate\":{\"cart\":{\"checkoutUrl\":\"https://shop.test/checkout\"}}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Quantity = 3;
        ctx.Session.Vars[ShopifyFlow.GraphQlTokenVar] = "tok";
        ctx.Session.Vars[ShopifyFlow.GraphQlCartVar] = "gid://shopify/Cart/1";
        ctx.Session.Vars["shopify.lineId"] = "gid://shopify/CartLine/9";
        ctx.Session.Vars["shopify.graphqlBase"] = server.BaseUrl + "/graphql";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.EditLineAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        var sent = Newtonsoft.Json.Linq.JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopifyGraphQl.CartLinesUpdate, sent["query"]!.ToObject<string>());
        Assert.Equal("gid://shopify/Cart/1", sent["variables"]!["cartId"]!.ToObject<string>());
        Assert.Equal("gid://shopify/CartLine/9", sent["variables"]!["lines"]![0]!["id"]!.ToObject<string>());
        Assert.Equal(3, sent["variables"]!["lines"]![0]!["quantity"]!.ToObject<int>());
    }

    /// <summary>
    /// Without a line id there is nothing for cartLinesUpdate to address, so the REST call this step has always
    /// made stays — the structured path is an addition, not a replacement.
    /// </summary>
    [Fact]
    public async Task WithoutALineIdTheRestCallRemains()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };
        ctx.Session.Quantity = 2;

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.EditLineAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.EndsWith("/cart/update.js", server.Requests[0].Path);
    }
}
