"""Wire the Shop app cart into the flow's add-to-cart, and test the message vocabulary."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/ShopAppCartTests.cs'

flow = io.open(FLOW, encoding='utf-8', newline='').read()
if 'ShopAppCart' not in flow:
    anchor = '        var createHost = c.Session.Vars.GetValueOrDefault("shopify.cartCreateHost");'
    if flow.count(anchor) != 1:
        raise SystemExit('anchor found %d times' % flow.count(anchor))

    branch = '''        // R1355: the Shop app's own cart, when the run carries a broker id and a variant. Different API from this
        // store's storefront cart above, so it is a branch with its own refusal messages.
        var shopBrokerId = c.Session.Vars.GetValueOrDefault("shopapp.brokerId");
        var shopVariantId = c.Session.Vars.GetValueOrDefault("shopapp.variantId");
        if (!string.IsNullOrEmpty(shopBrokerId) && !string.IsNullOrEmpty(shopVariantId))
        {
            var (shopCart, shopCartError) = await ShopAppCart.AddLineAsync(c, new JObject
            {
                ["brokerId"] = shopBrokerId,
                ["variantId"] = shopVariantId,
                ["quantity"] = int.TryParse(c.Session.Vars.GetValueOrDefault("shopapp.quantity"), out var qty)
                    ? qty
                    : c.Session.Quantity,
                ["attribution"] = JObject.Parse(
                    c.Session.Vars.GetValueOrDefault("shopapp.attribution") ?? "{}"),
            }, ct, c.Session.Vars.GetValueOrDefault("shopapp.url")).ConfigureAwait(false);

            if (shopCart is null) return StepOutcome.Fail(shopCartError);

            c.Session.Vars["cart"] = shopCart.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

'''
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow.replace(anchor, branch + anchor))
    print('wired the shop-app cart branch')

tests = '''using System.Threading.Tasks;
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
            (200, "{\\"data\\":{\\"cartLineItemSet\\":{\\"cart\\":{\\"errors\\":[{\\"message\\":\\"Variant is out of stock\\"}]}}}}"));
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
            (200, "{\\"data\\":{\\"cartLineItemSet\\":{\\"cart\\":{\\"id\\":\\"c-9\\"}}}}"));
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
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
