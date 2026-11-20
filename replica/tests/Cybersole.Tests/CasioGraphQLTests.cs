using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1312: Casio answers a Magento GraphQL document, and the selection it asks for is in the image.
///
/// <para>
/// The selection string is pinned byte for byte because it is the finding: three of its fields —
/// <c>casio_sales_type</c>, <c>casio_can_purchase</c>, <c>casio_sales_start_date</c> — are Casio's own sale
/// attributes and exist on no standard Magento type, which is why this store could not be read like an
/// ordinary catalogue page. The wrapper around the selection is inference and the tests say so by
/// exercising the composed document rather than claiming it is the image's.
/// </para>
/// </summary>
public sealed class CasioGraphQLTests
{
    [Fact]
    public void TheSelectionIsTheStringTheImageHolds()
    {
        Assert.Equal(274, CasioGraphQL.ObservedSelection.Length);
        Assert.StartsWith("\"]}},sort:{name:ASC},pageSize:40){items{sku name url_key", CasioGraphQL.ObservedSelection);
        Assert.EndsWith("total_count}}", CasioGraphQL.ObservedSelection);
    }

    [Fact]
    public void EveryFieldTheSelectionAsksForIsListed()
    {
        Assert.Equal(13, CasioGraphQL.Fields.Count);
        foreach (var field in new[]
                 {
                     "sku", "url_key", "only_x_left_in_stock", "casio_sales_type",
                     "casio_can_purchase", "casio_sales_start_date", "casio_sales_end_date", "casio_image_url",
                 })
        {
            Assert.Contains(field, CasioGraphQL.Fields);
            Assert.Contains(field, CasioGraphQL.ObservedSelection);
        }

        Assert.Equal(40, CasioGraphQL.PageSize);
        Assert.Equal("{name:ASC}", CasioGraphQL.Sort);
        Assert.Equal("/graphql", CasioGraphQL.Path);
    }

    /// <summary>The page size in the constant must be the one in the string, not a second copy of it.</summary>
    [Fact]
    public void ThePageSizeIsTheOneInTheSelection()
    {
        Assert.Contains($"pageSize:{CasioGraphQL.PageSize}", CasioGraphQL.ObservedSelection);
        Assert.Contains("sort:" + CasioGraphQL.Sort, CasioGraphQL.ObservedSelection);
    }

    [Fact]
    public void TheDocumentCarriesTheSelectionAndEscapesTheSku()
    {
        var document = CasioGraphQL.SearchDocument("G-SHOCK \"Limited\"");

        Assert.StartsWith("query{products(filter:{sku:{in:[\"", document);
        Assert.Contains("G-SHOCK \\\"Limited\\\"", document);
        Assert.EndsWith(CasioGraphQL.ObservedSelection, document);
    }

    [Fact]
    public void AProductIsReadOutOfTheReplyWithItsSaleWindow()
    {
        var reply = JObject.Parse(@"{
            ""data"": { ""products"": { ""total_count"": 1, ""items"": [{
                ""sku"": ""GA-2100-1A"",
                ""name"": ""G-SHOCK GA-2100"",
                ""url_key"": ""g-shock-ga-2100"",
                ""stock_status"": ""IN_STOCK"",
                ""only_x_left_in_stock"": null,
                ""casio_sales_type"": ""PREORDER"",
                ""casio_can_purchase"": ""false"",
                ""casio_sales_start_date"": ""2026-12-01 00:00:00"",
                ""casio_sales_end_date"": ""2026-12-31 00:00:00"",
                ""casio_image_url"": ""https://www.casio.com/i/ga2100.jpg"",
                ""image"": { ""label"": ""G-SHOCK"" },
                ""price_range"": { ""minimum_price"": { ""final_price"": { ""value"": 99.0, ""currency"": ""USD"" } } }
            }] } }
        }");

        var product = CasioGraphQL.ReadProduct(reply);

        Assert.NotNull(product);
        Assert.Equal("GA-2100-1A", product!.Sku);
        Assert.Equal("PREORDER", product.SalesType);
        Assert.Equal("2026-12-01 00:00:00", product.SalesStart);
        Assert.Equal("USD", product.Currency);
        Assert.Equal("1", product.TotalCount);
        // In stock, but the store's own attribute says it cannot be bought: the attribute wins.
        Assert.False(CasioGraphQL.CanBuy(product));
    }

    [Fact]
    public void WithoutTheAttributeStockStatusDecides()
    {
        var product = new CasioProduct { StockStatus = "IN_STOCK" };
        Assert.True(CasioGraphQL.CanBuy(product));

        var outOfStock = new CasioProduct { StockStatus = "OUT_OF_STOCK" };
        Assert.False(CasioGraphQL.CanBuy(outOfStock));
    }

    [Theory]
    [InlineData("{\"data\":{\"products\":{\"items\":[]}}}")]
    [InlineData("{\"errors\":[{\"message\":\"nope\"}]}")]
    [InlineData("{}")]
    public void AnEmptyOrFailedReplyIsNoProduct(string json)
    {
        Assert.Null(CasioGraphQL.ReadProduct(JObject.Parse(json)));
        Assert.Null(CasioGraphQL.ReadProduct(null));
    }

    [Fact]
    public async Task TheSearchPostsTheDocumentAndReadsTheAnswer()
    {
        var item = "{\"sku\":\"GA-2100-1A\",\"name\":\"G-SHOCK\",\"stock_status\":\"IN_STOCK\",\"casio_can_purchase\":\"true\"}";
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"products\":{\"total_count\":1,\"items\":[" + item + "]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/x" };

        var product = await CasioGraphQL.SearchAsync(ctx, "GA-2100-1A", default, server.BaseUrl + "/graphql");

        Assert.NotNull(product);
        Assert.Equal("GA-2100-1A", product!.Sku);
        Assert.True(CasioGraphQL.CanBuy(product));
        Assert.Equal("/graphql", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Contains("casio_can_purchase", sent["query"]!.Value<string>());
    }

    /// <summary>
    /// The flow asks GraphQL first and falls back to the page. The fallback matters: a store that answers
    /// the document with an error should not stop the flow from reading the product page it read before.
    /// </summary>
    [Fact]
    public async Task TheFlowFallsBackToThePageWhenGraphQlAnswersNothing()
    {
        using var server = new TinyServer((req, _) =>
            (req.RawUrl ?? string.Empty).Contains("/graphql", System.StringComparison.Ordinal)
                ? (200, "{\"errors\":[{\"message\":\"nope\"}]}")
                : (200, "<html><title>G-SHOCK GA-2100</title><span>$99.00</span></html>"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/ga-2100" };
        ctx.Session.Vars["casio.sku"] = "GA-2100-1A";
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("G-SHOCK GA-2100", ctx.Session.Vars["product"]);
        Assert.Equal("99.00", ctx.Session.Vars["price"]);
        Assert.False(ctx.Session.Vars.ContainsKey("casio.canPurchase"));
    }

    [Fact]
    public async Task TheFlowUsesTheStructuredAnswerWhenThereIsOne()
    {
        var item = "{\"sku\":\"GA-2100-1A\",\"name\":\"G-SHOCK\",\"stock_status\":\"IN_STOCK\"," +
                   "\"casio_can_purchase\":\"true\",\"casio_sales_start_date\":\"2026-01-01\"}";
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"products\":{\"total_count\":1,\"items\":[" + item + "]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/products/ga-2100" };
        ctx.Session.Vars["casio.sku"] = "GA-2100-1A";
        ctx.Session.Vars["casio.graphqlPath"] = server.BaseUrl + "/graphql";

        var outcome = await new CasioFlow().FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("GA-2100-1A", ctx.Session.Vars["sku"]);
        Assert.Equal("true", ctx.Session.Vars["casio.canPurchase"]);
        Assert.Equal("2026-01-01", ctx.Session.Vars["casio.salesStart"]);
        // One request only: the page was never fetched.
        Assert.Single(server.Requests);
    }
}
