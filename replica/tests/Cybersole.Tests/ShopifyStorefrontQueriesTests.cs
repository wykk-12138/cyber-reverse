using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1348/R1349: the Shopify Storefront operations the image carries. The token the image holds as a literal is a
/// credential, so it is the caller's here — a test that needed it baked in would be a test that shipped it.
/// </summary>
public sealed class ShopifyStorefrontQueriesTests
{
    [Fact]
    public void TheThreeDocumentsAreTheOnesWithAStorefrontSignature()
    {
        Assert.Equal(5876, ShopifyStorefrontQueries.CartApiObjectCreate.Length);
        Assert.Equal(1622, ShopifyStorefrontQueries.CreateCart.Length);
        Assert.Equal(1553, ShopifyStorefrontQueries.RemoveLineItemFromCart.Length);

        Assert.StartsWith("mutation cartApiObjectCreate($input: CartInput!",
            ShopifyStorefrontQueries.CartApiObjectCreate);
        Assert.StartsWith("mutation createCart($lines: [CartLineInput!]!",
            ShopifyStorefrontQueries.CreateCart);
        Assert.StartsWith("mutation removeLineItemFromCart($cartId: String!",
            ShopifyStorefrontQueries.RemoveLineItemFromCart);
    }

    [Fact]
    public void TheDeclaredSetsAreTheDocumentsOwn()
    {
        Assert.Equal(8, ShopifyStorefrontQueries.Declared["cartApiObjectCreate"].Length);
        Assert.Equal(7, ShopifyStorefrontQueries.SenderFills["cartApiObjectCreate"].Length);
        Assert.DoesNotContain("metafieldsIdentifiers", ShopifyStorefrontQueries.SenderFills["cartApiObjectCreate"]);

        Assert.Equal(new[] { "lines", "buyerIdentity", "attributes", "country", "language" },
            ShopifyStorefrontQueries.Declared["createCart"]);
        Assert.Equal(new[] { "cartId", "lineItemId", "version", "quantity", "locale" },
            ShopifyStorefrontQueries.Declared["removeLineItemFromCart"]);
    }

    [Fact]
    public async Task NoHostMeansNoRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyStorefrontQueries.SendAsync(
            ctx, null, "token", "createCart", new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no store host", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task NoTokenMeansNoRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyStorefrontQueries.SendAsync(
            ctx, "shop.test", null, "createCart", new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no storefront access token", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>A variable the document does not declare is refused here, not by the server.</summary>
    [Fact]
    public async Task AnUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await ShopifyStorefrontQueries.SendAsync(
            ctx, "shop.test", "token", "createCart", new JObject { ["input"] = "x" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $input", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>setBillingAddress is not in this class: its variables belong to the tm-api family.</summary>
    [Fact]
    public void SetBillingAddressIsNotAStorefrontOperation()
    {
        Assert.Null(ShopifyStorefrontQueries.DocumentFor("setBillingAddress"));
        Assert.NotNull(ShopifyStorefrontQueries.DocumentFor("createCart"));
    }
}
