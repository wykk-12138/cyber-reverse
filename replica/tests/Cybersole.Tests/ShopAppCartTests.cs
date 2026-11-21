using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1355: the Shop app cart. The document is one half; the other half is the set of outcomes its handler
/// distinguishes, and those are what these tests pin.
/// </summary>
public sealed class ShopAppCartTests
{
    [Fact]
    public void TheDocumentAndItsFourVariables()
    {
        Assert.Equal(1255, ShopAppCart.Document.Length);
        Assert.StartsWith("mutation CartLineItemSet(", ShopAppCart.Document);
        Assert.Equal(new[] { "brokerId", "variantId", "quantity", "attribution" }, ShopAppCart.DeclaredVariables);
        Assert.Equal("cartLineItemSet", ShopAppCart.OperationName);
    }

    /// <summary>The handler's own words, which a faithful replica must produce too.</summary>
    [Fact]
    public void TheHandlerVocabularyIsKeptVerbatim()
    {
        Assert.Equal("Password page up", ShopAppCart.PasswordPageMessage);
        Assert.Equal("The product in the cart does not exist.", ShopAppCart.ProductMissingMessage);
        Assert.Equal("The product in the cart is out of stock.", ShopAppCart.ProductOutOfStockMessage);
        Assert.Equal("The shopify shop of this cart is not eligible", ShopAppCart.ShopNotEligibleMessage);
        Assert.Equal("cannot be fulfilled", ShopAppCart.CannotBeFulfilledMessage);
        Assert.Equal("tries exhausted on cart", ShopAppCart.TriesExhaustedMessage);
    }

    [Fact]
    public async Task WithoutABrokerIdNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cart, error) = await ShopAppCart.AddLineAsync(ctx, new JObject(), default);

        Assert.Null(cart);
        Assert.Contains("no brokerId", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task WithoutAVariantIdNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cart, error) = await ShopAppCart.AddLineAsync(
            ctx, new JObject { ["brokerId"] = "b-1" }, default);

        Assert.Null(cart);
        Assert.Contains("no variantId", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>An out-of-stock reply becomes the handler's out-of-stock message, not a raw GraphQL string.</summary>
    [Fact]
    public async Task AnOutOfStockReplyBecomesTheHandlersOwnMessage()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"cartLineItemSet\":{\"cart\":{\"errors\":[{\"message\":\"Variant is out of stock\"}]}}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cart, error) = await ShopAppCart.AddLineAsync(
            ctx, new JObject { ["brokerId"] = "b-1", ["variantId"] = "v-1" }, default,
            server.BaseUrl + "/graphql");

        Assert.Null(cart);
        Assert.Equal(ShopAppCart.ProductOutOfStockMessage, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("cartLineItemSet", sent["operationName"]!.ToObject<string>());
        Assert.Equal(ShopAppCart.Document, sent["query"]!.ToObject<string>());
    }

    [Fact]
    public async Task AGoodReplyReturnsTheCart()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"cartLineItemSet\":{\"cart\":{\"id\":\"c-9\"}}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cart, error) = await ShopAppCart.AddLineAsync(
            ctx, new JObject { ["brokerId"] = "b-1", ["variantId"] = "v-1" }, default,
            server.BaseUrl + "/graphql");

        Assert.NotNull(cart);
        Assert.Equal(string.Empty, error);
        Assert.Equal("c-9", cart!["id"]!.ToObject<string>());
    }
}
