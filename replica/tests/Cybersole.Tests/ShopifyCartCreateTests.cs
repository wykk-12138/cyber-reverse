using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1348: Shopify Storefront cart creation, from the sender at sub_140D1B380. The image's storefront token is a
/// credential, so it is the caller's here — a test that needed it baked in would be a test that shipped it.
/// </summary>
public sealed class ShopifyCartCreateTests
{
    [Fact]
    public void TheDocumentAndVariablesAreTheObservedOnes()
    {
        Assert.Equal("cartApiObjectCreate", ShopifyCartCreate.OperationName);
        Assert.Equal(5876, ShopifyCartCreate.Document.Length);
        Assert.StartsWith("mutation cartApiObjectCreate($input: CartInput!", ShopifyCartCreate.Document);
        Assert.Equal(8, ShopifyCartCreate.DeclaredVariables.Length);
        Assert.Equal(7, ShopifyCartCreate.SenderVariables.Length);
        Assert.Contains("metafieldsIdentifiers", ShopifyCartCreate.DeclaredVariables);
        Assert.DoesNotContain("metafieldsIdentifiers", ShopifyCartCreate.SenderVariables);
    }

    [Fact]
    public async Task NoHostMeansNoRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cartId, error) = await ShopifyCartCreate.CreateAsync(
            ctx, null, "token", new JObject { ["input"] = new JObject() }, default);

        Assert.Null(cartId);
        Assert.Contains("no store host", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task NoTokenMeansNoRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cartId, error) = await ShopifyCartCreate.CreateAsync(
            ctx, "shop.test", null, new JObject { ["input"] = new JObject() }, default);

        Assert.Null(cartId);
        Assert.Contains("no storefront access token", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task NoInputMeansNoRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (cartId, error) = await ShopifyCartCreate.CreateAsync(
            ctx, "shop.test", "token", new JObject(), default);

        Assert.Null(cartId);
        Assert.Contains("no $input", error);
        Assert.Empty(server.Requests);
    }
}
