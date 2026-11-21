"""R1329: give CustomerCartDocument a caller — it has had none since R1320.

Source-level fact, not a search: CustomerCartDocument appears exactly once in src, at its own declaration, and
otherwise only in tests. A document with no caller is a document the replica cannot send, and in an AOT build
it is also the kind of thing that quietly disappears (R1310). So this wires the observed 61-character query
into CasioFlow.GetCartAsync, a base step every flow already exposes.

It also fills one of the absent store-family names from the async tail — the cart-read step — with the query
the image carries rather than an invented one.

Usage: python analysis/add_cart_read.py
"""
import io

CART = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

cart = io.open(CART, encoding='utf-8', newline='').read()

if 'ReadCartAsync' in cart:
    raise SystemExit('reader already present')

anchor = '    private static async Task<JObject?> PostAsync(FlowContext c, string endpoint, JObject body, CancellationToken ct)'
if cart.count(anchor) != 1:
    raise SystemExit('PostAsync anchor found %d times' % cart.count(anchor))

reader = (
    '    /// <summary>\n'
    '    /// Read the customer cart — the 61-character <see cref="CustomerCartDocument"/> the image carries at\n'
    '    /// 0x14718FB74. R1329: the constant had no caller from R1320 until this, which made it a document the\n'
    '    /// replica could not actually send.\n'
    '    /// </summary>\n'
    '    public static async Task<MagentoCartResult> ReadCartAsync(\n'
    '        FlowContext c, string endpoint, CancellationToken ct)\n'
    '    {\n'
    '        var reply = await PostAsync(c, endpoint, Body(CustomerCartDocument), ct).ConfigureAwait(false);\n'
        '        if (reply is null) return MagentoCartResult.Fail("cart: no reply");\n'
    '\n'
    '        if (reply["errors"] is JArray topLevel && topLevel.Count > 0)\n'
    '            return MagentoCartResult.Fail("cart: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));\n'
    '\n'
    '        var customerCart = reply["data"]?["customerCart"];\n'
    '        if (customerCart is null)\n'
    '            return MagentoCartResult.Fail("cart: no customerCart in reply — this store may key carts by masked id");\n'
    '\n'
    '        return new MagentoCartResult\n'
    '        {\n'
    '            Ok = true,\n'
    '            CartId = customerCart["id"]?.ToString() ?? string.Empty,\n'
    '            TotalQuantity = customerCart["total_quantity"]?.ToString() ?? string.Empty,\n'
    '        };\n'
    '    }\n'
    '\n'
)

cart = cart.replace(anchor, reader + anchor)
io.open(CART, 'w', encoding='utf-8', newline='').write(cart)
print('added MagentoCart.ReadCartAsync')

flows = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'public override async Task<StepOutcome> GetCartAsync' in flows:
    raise SystemExit('a GetCartAsync override already exists somewhere in this file — check before adding')

step_anchor = '    /// <summary>\n    /// Set the billing address through Magento\'s <c>updateMyCart</c> mutation.'
if flows.count(step_anchor) != 1:
    raise SystemExit('billing doc-comment anchor found %d times' % flows.count(step_anchor))

step = (
    '    /// <summary>\n'
    '    /// Read the cart through the image\'s own 61-character query.\n'
    '    ///\n'
    '    /// <para>\n'
    '    /// <b>Observed:</b> <c>{ customerCart { id total_quantity items { uid quantity } } }</c> at 0x14718FB74.\n'
    '    /// <b>Inference:</b> that this store answers it at the same <c>/graphql</c> endpoint as the cart\n'
    '    /// mutations; <c>casio.graphqlPath</c> overrides it. A store that keys carts by masked id answers no\n'
    '    /// <c>customerCart</c>, and the step says so rather than reporting an empty cart.\n'
    '    /// </para>\n'
    '    /// </summary>\n'
    '    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)\n'
    '    {\n'
    '        var endpoint = c.Session.Vars.GetValueOrDefault("casio.graphqlPath");\n'
    '        if (string.IsNullOrEmpty(endpoint))\n'
    '            endpoint = Payments.GatewayHttp.OriginOf(c.Url) + CasioGraphQL.Path;\n'
    '\n'
    '        var result = await MagentoCart.ReadCartAsync(c, endpoint!, ct).ConfigureAwait(false);\n'
    '        if (!result.Ok) return StepOutcome.Fail(result.Error);\n'
    '\n'
    '        if (!string.IsNullOrEmpty(result.CartId)) c.Session.Vars["cart"] = result.CartId;\n'
    '        c.Session.Vars["casio.cartTotal"] = result.TotalQuantity;\n'
    '        c.Emit("casio: cart " + result.CartId + " holds " + result.TotalQuantity, "StatusInfo");\n'
    '        return StepOutcome.Success();\n'
    '    }\n'
    '\n'
)
flows = flows.replace(step_anchor, step + step_anchor)
io.open(FLOWS, 'w', encoding='utf-8', newline='').write(flows)
print('added CasioFlow.GetCartAsync')
