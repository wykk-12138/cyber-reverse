"""R1377c: make the two Magento documents whole, and give them production callers.

Two guards caught real problems with what I moved:

    EveryDocumentConstantIsWhole            BuyNowDocument was cut at a quote inside the body
    EveryDocumentConstantHasAProductionCaller   neither document had a caller — a constant is not a feature

So the bodies come from the stored documents rather than from a substring of the file, and both get a method that sends
them, reached from MagentoFlow's cart step.
"""
import io
import json

DOCS = 'analysis/.block_a_docs.json'
CART = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/MagentoFlow.cs'

stored = json.loads(io.open(DOCS, encoding='utf-8').read())
add_document = stored['last_addToCart']
buy_document = stored['last_buynow']
print('stored lengths: addToCart=%d buynow=%d' % (len(add_document), len(buy_document)))


def verbatim(text):
    return text.replace('"', '""')


cart = io.open(CART, encoding='utf-8', newline='').read()

for name, document in (('AddToCartDocument', add_document), ('BuyNowDocument', buy_document)):
    start = cart.find('public const string %s = @"' % name)
    if start < 0:
        raise SystemExit('%s not found' % name)
    body_start = start + len('public const string %s = @"' % name)
    body_end = cart.find('";', body_start)
    if body_end < 0:
        raise SystemExit('%s has no terminator' % name)
    cart = cart[:body_start] + verbatim(document) + cart[body_end:]

print('both bodies rewritten from the stored documents')

methods = '''
    /// <summary>
    /// Add a line through the image's own addToCart document. The four variables are the document's: sku, qty, type
    /// and info.
    /// </summary>
    public static Task<(JObject? Data, string Error)> AddToCartAsync(
        FlowContext c, string endpoint, string sku, int qty, string type, JObject? info, CancellationToken ct) =>
        SendDocumentAsync(c, endpoint, FillAddToCart(sku, qty, type, info), ct);

    /// <summary>
    /// Buy now through the image's own document. It declares nothing, so the item travels in the document's own
    /// literal and only the quote id a caller already holds is substituted.
    /// </summary>
    public static Task<(JObject? Data, string Error)> BuyNowAsync(
        FlowContext c, string endpoint, string quoteId, CancellationToken ct) =>
        SendDocumentAsync(c, endpoint,
            BuyNowDocument.Replace("quote_id: \\"1\\"", "quote_id: \\"" + quoteId + "\\""), ct);

    /// <summary>The four-variable body for addToCart.</summary>
    public static JObject FillAddToCart(string sku, int qty, string type, JObject? info) => new()
    {
        ["query"] = AddToCartDocument,
        ["variables"] = new JObject
        {
            ["sku"] = sku,
            ["qty"] = qty,
            ["type"] = type,
            ["info"] = info ?? new JObject(),
        },
    };

    /// <summary>Post a body the caller already built and unwrap the usual envelope.</summary>
    private static async Task<(JObject? Data, string Error)> SendDocumentAsync(
        FlowContext c, string? endpoint, JObject body, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(endpoint)) return (null, "magento: no endpoint");

        try
        {
            var reply = await PostAsync(c, endpoint!.TrimEnd('/'), body, ct).ConfigureAwait(false);
            if (reply is null) return (null, "magento: no reply");

            if (reply["errors"] is JArray topLevel && topLevel.Count > 0)
                return (null, "magento: " + (topLevel[0]?["message"]?.ToString() ?? "graphql error"));

            var data = reply["data"] as JObject;
            return data is null ? (null, "magento: no data in reply") : (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "magento: " + ex.GetType().Name);
        }
    }
}
'''

cart = cart.rstrip()
cart = cart[:cart.rfind('}')].rstrip('\n') + '\n' + methods
io.open(CART, 'w', encoding='utf-8', newline='').write(cart)
print('three methods added to MagentoCart')

flow = io.open(FLOW, encoding='utf-8', newline='').read()
if 'BuyNowAsync' not in flow:
    marker = 'public override'
    position = flow.find('AddToCartAsync')
    if position < 0:
        raise SystemExit('MagentoFlow.AddToCartAsync not found')
    line_start = flow.rfind('\n', 0, position)
    body = flow.find('{', position)
    branch = '''
        // R1377: the two documents the guards asked for a caller for. The endpoint is the store's own /graphql; the
        // sku, quantity and quote id come from the run.
        var magentoEndpoint = c.Session.Vars.GetValueOrDefault("magento.endpoint");
        if (!string.IsNullOrEmpty(magentoEndpoint))
        {
            var sku = c.Session.Vars.GetValueOrDefault("magento.sku");
            var quoteId = c.Session.Vars.GetValueOrDefault("magento.quoteId");
            if (!string.IsNullOrEmpty(sku))
            {
                var qty = int.TryParse(c.Session.Vars.GetValueOrDefault("magento.qty"), out var parsed) ? parsed : 1;
                var (addData, addError) = await MagentoCart
                    .AddToCartAsync(c, magentoEndpoint!, sku!, qty,
                        c.Session.Vars.GetValueOrDefault("magento.type") ?? "Simple", null, ct)
                    .ConfigureAwait(false);
                if (addData is null) return StepOutcome.Fail(addError);

                c.Session.Vars["magentoCart"] = addData.ToString(Newtonsoft.Json.Formatting.None);
                return StepOutcome.Success();
            }

            if (!string.IsNullOrEmpty(quoteId))
            {
                var (buyData, buyError) = await MagentoCart
                    .BuyNowAsync(c, magentoEndpoint!, quoteId!, ct).ConfigureAwait(false);
                if (buyData is null) return StepOutcome.Fail(buyError);

                c.Session.Vars["magentoBuyNow"] = buyData.ToString(Newtonsoft.Json.Formatting.None);
                return StepOutcome.Success();
            }
        }
'''
    flow = flow[:body + 1] + branch + flow[body + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
    print('MagentoFlow.AddToCartAsync now sends both documents')
