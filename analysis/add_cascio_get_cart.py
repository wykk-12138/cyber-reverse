"""R1329 (continued): add CasioFlow.GetCartAsync, now that which_class_has.py says Casio does not have one.

The anchor is the billing doc-comment written in R1321, which is unique to CasioFlow, so the insertion lands in
the right class rather than merely in the right file.

Usage: python analysis/add_cascio_get_cart.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'public override async Task<StepOutcome> GetCartAsync' in text.split("class CasioFlow")[1].split('\npublic sealed class ')[0]:
    raise SystemExit('CasioFlow already has GetCartAsync')

anchor = "    /// <summary>\n    /// Set the billing address through Magento's <c>updateMyCart</c> mutation."
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

step = (
    '    /// <summary>\n'
    '    /// Read the cart through the image\'s own 61-character query.\n'
    '    ///\n'
    '    /// <para>\n'
    '    /// <b>Observed:</b> <c>{ customerCart { id total_quantity items { uid quantity } } }</c> at 0x14718FB74.\n'
    '    /// <b>Inference:</b> that this store answers it at the same <c>/graphql</c> endpoint its cart mutations\n'
    '    /// use; <c>casio.graphqlPath</c> overrides it. A store that keys carts by masked id answers no\n'
    '    /// <c>customerCart</c>, and the step says so rather than reporting an empty cart as a success.\n'
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

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(anchor, step + anchor))
print('added CasioFlow.GetCartAsync')
