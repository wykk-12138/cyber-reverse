using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1342: Shopify's Shop app product query, from the sender at sub_140D26A20. It is the largest document the
/// project carries, so these also check that a 26 KB constant survives source, compiler and AOT.
/// </summary>
public sealed class ShopAppProductTests
{
    [Fact]
    public void TheEndpointAndOperationAreTheObservedOnes()
    {
        Assert.Equal("https://server.shop.app/graphql", ShopAppProduct.Url);
        Assert.Equal("ProductDetails", ShopAppProduct.OperationName);
        Assert.Equal("RECOMMENDED", ShopAppProduct.SortRecommended);
        Assert.Equal(31, ShopAppProduct.Url.Length);
    }

    [Fact]
    public void TheDocumentIsTheWholeStringTheImageHolds()
    {
        Assert.Equal(26206, ShopAppProduct.Document.Length);
        Assert.StartsWith("query ProductDetails(", ShopAppProduct.Document);
        // The document ends in a closing brace, a CRLF and trailing spaces — measured, not assumed.
        Assert.EndsWith("                        ", ShopAppProduct.Document);
        // The body is fragments over a product; if it were truncated the fragment set would be short.
        Assert.Contains("fragment ", ShopAppProduct.Document);
        Assert.DoesNotContain("[26206 chars total]", ShopAppProduct.Document);
    }

    [Fact]
    public void TheEightVariableNamesAreTheSenders()
    {
        Assert.Equal(8, ShopAppProduct.VariableNames.Length);
        foreach (var name in new[]
                 {
                     "productId", "productInput", "brokerId", "imageWidth", "sampleReviews",
                     "sortReviewsBy", "userHasEntryPointsV2", "variantsLimit",
                 })
        {
            Assert.Contains(name, ShopAppProduct.VariableNames);
            Assert.Contains("$" + name, ShopAppProduct.Document);
        }
    }

    [Fact]
    public void TheEnvelopeCarriesTheThreeObservedKeys()
    {
        var body = ShopAppProduct.Envelope(new JObject { ["brokerId"] = "b" });

        Assert.Equal("ProductDetails", body["operationName"]!.ToObject<string>());
        Assert.Equal(ShopAppProduct.Document, body["query"]!.ToObject<string>());
        Assert.Equal("b", body["variables"]!["brokerId"]!.ToObject<string>());
    }

    /// <summary>No identifiers means no query: the document would ask about nothing in particular.</summary>
    [Fact]
    public async Task WithoutVariablesNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await ShopAppProduct.FetchAsync(ctx, new JObject(), default);

        Assert.Null(product);
        Assert.Contains("no variables", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsTheObservedEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"product\":{\"id\":\"gid://shop/1\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (product, error) = await ShopAppProduct.FetchAsync(
            ctx, new JObject { ["brokerId"] = "broker-1", ["imageWidth"] = 800 }, default,
            server.BaseUrl + "/graphql");

        Assert.NotNull(product);
        Assert.Equal(string.Empty, error);
        Assert.Equal("gid://shop/1", product!["id"]!.ToObject<string>());
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(ShopAppProduct.Document, sent["query"]!.ToObject<string>());
        Assert.Equal("broker-1", sent["variables"]!["brokerId"]!.ToObject<string>());
    }
}
