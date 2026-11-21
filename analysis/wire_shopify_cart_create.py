"""R1348: wire the cart creation into ShopifyFlow's add-to-cart, plus tests."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/ShopifyCartCreateTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'ShopifyCartCreate' not in text:
    anchor = '    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)'
    if text.count(anchor) != 1:
        raise SystemExit('add-to-cart anchor found %d times' % text.count(anchor))

    branch = '''    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1348: the Storefront cart creation, when the run supplies a host, a token and a CartInput. The image's
        // own storefront token is a credential and is deliberately not copied into source.
        var createHost = c.Session.Vars.GetValueOrDefault("shopify.cartCreateHost");
        var createToken = c.Session.Vars.GetValueOrDefault(ShopifyHeaders.StorefrontAccessToken);
        var createInput = c.Session.Vars.GetValueOrDefault("shopify.cartCreateInput");
        if (!string.IsNullOrEmpty(createHost) && !string.IsNullOrEmpty(createToken) &&
            !string.IsNullOrWhiteSpace(createInput))
        {
            Newtonsoft.Json.Linq.JObject input;
            try
            {
                input = Newtonsoft.Json.Linq.JObject.Parse(createInput!);
            }
            catch (Newtonsoft.Json.JsonException)
            {
                return StepOutcome.Fail("shopify: shopify.cartCreateInput is not valid JSON");
            }

            var variables = new Newtonsoft.Json.Linq.JObject
            {
                ["input"] = input,
                ["includeInventory"] = false,
                ["includeStoreAvailability"] = true,
                ["includeSellingPlans"] = true,
                ["includeProductTags"] = false,
                ["includeCustomerTags"] = false,
                ["country"] = c.ProfileData?.Country ?? c.Session.Vars.GetValueOrDefault("country"),
            };

            var (cartId, createError) = await ShopifyCartCreate
                .CreateAsync(c, createHost, createToken, variables, ct)
                .ConfigureAwait(false);
            if (cartId is null) return StepOutcome.Fail(createError);

            c.Session.Vars[GraphQlCartVar] = cartId;
            return StepOutcome.Success();
        }

'''

    text = text.replace(anchor, branch + anchor.rstrip('\n') + '\n', 1) if False else text
    # The replacement above must keep the original method signature, so insert the branch *inside* it instead.
    body_start = text.find(anchor) + len(anchor) + len('\n    {')
    insert = '''
        // R1348: the Storefront cart creation, when the run supplies a host, a token and a CartInput. The image's
        // own storefront token is a credential and is deliberately not copied into source.
        var createHost = c.Session.Vars.GetValueOrDefault("shopify.cartCreateHost");
        var createToken = c.Session.Vars.GetValueOrDefault(ShopifyHeaders.StorefrontAccessToken);
        var createInput = c.Session.Vars.GetValueOrDefault("shopify.cartCreateInput");
        if (!string.IsNullOrEmpty(createHost) && !string.IsNullOrEmpty(createToken) &&
            !string.IsNullOrWhiteSpace(createInput))
        {
            Newtonsoft.Json.Linq.JObject input;
            try
            {
                input = Newtonsoft.Json.Linq.JObject.Parse(createInput!);
            }
            catch (Newtonsoft.Json.JsonException)
            {
                return StepOutcome.Fail("shopify: shopify.cartCreateInput is not valid JSON");
            }

            var createVariables = new Newtonsoft.Json.Linq.JObject
            {
                ["input"] = input,
                ["includeInventory"] = false,
                ["includeStoreAvailability"] = true,
                ["includeSellingPlans"] = true,
                ["includeProductTags"] = false,
                ["includeCustomerTags"] = false,
                ["country"] = c.ProfileData?.Country ?? c.Session.Vars.GetValueOrDefault("country"),
            };

            var (createdCartId, createError) = await ShopifyCartCreate
                .CreateAsync(c, createHost, createToken, createVariables, ct)
                .ConfigureAwait(false);
            if (createdCartId is null) return StepOutcome.Fail(createError);

            c.Session.Vars[GraphQlCartVar] = createdCartId;
            return StepOutcome.Success();
        }
'''
    text = text[:body_start] + insert + text[body_start:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('wired the cart creation into AddToCartAsync')

tests = '''using System.Threading.Tasks;
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
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
