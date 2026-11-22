"""R1377d: redo the Magento work with the helper, after restoring the files I broke.

What went wrong: I appended methods with `rfind('}')`, which is the file's last brace, so they landed outside the class
— BuyNowDocument, AddToCartDocument and PostAsync all "did not exist". That is the third time this project has paid for
that exact line, so the fix is now `analysis/insert_into_class.py` rather than another retyped snippet.
"""
import io
import json
import subprocess
import sys

sys.path.insert(0, 'analysis')
from insert_into_class import insert_before_class_end  # noqa: E402

CART = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/MagentoFlow.cs'
DOCS = 'analysis/.block_a_docs.json'

for path in (CART, FLOW):
    blob = subprocess.run(['git', 'show', 'HEAD:' + path], capture_output=True).stdout
    io.open(path, 'wb').write(blob)
print('restored both files from HEAD')

stored = json.loads(io.open(DOCS, encoding='utf-8').read())
add_document = stored['last_addToCart']
buy_document = stored['last_buynow']


def verbatim(text):
    return text.replace('"', '""')


cart = io.open(CART, encoding='utf-8', newline='').read()

# 1. Both documents, whole, written at the class's own anchor.
anchor = '    public const string CustomerCartDocument ='
if cart.count(anchor) != 1:
    raise SystemExit('anchor matched %d times' % cart.count(anchor))

blocks = '''    /// <summary>
    /// addToCart, 232 characters. Declares $sku, $qty, $type and $info.
    /// </summary>
    public const string AddToCartDocument = @"%s";

    /// <summary>
    /// buynow, 216 characters, a query with no variables: the item travels in the document itself and answers with
    /// cart_id and session_id.
    /// </summary>
    public const string BuyNowDocument = @"%s";

''' % (verbatim(add_document), verbatim(buy_document))

cart = cart.replace(anchor, blocks + anchor, 1)

# 2. Methods, inserted inside the class.
methods = '''
    /// <summary>Add a line through the image's own addToCart document.</summary>
    public static Task<(JObject? Data, string Error)> AddToCartAsync(
        FlowContext c, string endpoint, string sku, int qty, string type, JObject? info, CancellationToken ct) =>
        SendDocumentAsync(c, endpoint, new JObject
        {
            ["query"] = AddToCartDocument,
            ["variables"] = new JObject
            {
                ["sku"] = sku,
                ["qty"] = qty,
                ["type"] = type,
                ["info"] = info ?? new JObject(),
            },
        }, ct);

    /// <summary>Buy now through the image's own document, substituting only the quote id.</summary>
    public static Task<(JObject? Data, string Error)> BuyNowAsync(
        FlowContext c, string endpoint, string quoteId, CancellationToken ct) =>
        SendDocumentAsync(c, endpoint, new JObject
        {
            ["query"] = BuyNowDocument.Replace("quote_id: \\"1\\"", "quote_id: \\"" + quoteId + "\\""),
        }, ct);

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
'''

cart = insert_before_class_end(cart, 'public static class MagentoCart', methods)
io.open(CART, 'w', encoding='utf-8', newline='').write(cart)
print('documents and methods now inside MagentoCart')

# 3. The caller.
flow = io.open(FLOW, encoding='utf-8', newline='').read()
position = flow.find('AddToCartAsync')
if position < 0:
    raise SystemExit('MagentoFlow.AddToCartAsync not found')
body = flow.find('{', position)

branch = '''
        // R1377: callers for the two documents the guards asked about. The endpoint is the store's own /graphql; the
        // sku, quantity and quote id come from the run.
        var magentoEndpoint = c.Session.Vars.GetValueOrDefault("magento.endpoint");
        if (!string.IsNullOrEmpty(magentoEndpoint))
        {
            var magentoSku = c.Session.Vars.GetValueOrDefault("magento.sku");
            if (!string.IsNullOrEmpty(magentoSku))
            {
                var quantity = int.TryParse(c.Session.Vars.GetValueOrDefault("magento.qty"), out var parsed) ? parsed : 1;
                var (addData, addError) = await MagentoCart
                    .AddToCartAsync(c, magentoEndpoint!, magentoSku!, quantity,
                        c.Session.Vars.GetValueOrDefault("magento.type") ?? "Simple", null, ct)
                    .ConfigureAwait(false);
                if (addData is null) return StepOutcome.Fail(addError);

                c.Session.Vars["magentoCart"] = addData.ToString(Newtonsoft.Json.Formatting.None);
                return StepOutcome.Success();
            }

            var magentoQuote = c.Session.Vars.GetValueOrDefault("magento.quoteId");
            if (!string.IsNullOrEmpty(magentoQuote))
            {
                var (buyData, buyError) = await MagentoCart
                    .BuyNowAsync(c, magentoEndpoint!, magentoQuote!, ct).ConfigureAwait(false);
                if (buyData is null) return StepOutcome.Fail(buyError);

                c.Session.Vars["magentoBuyNow"] = buyData.ToString(Newtonsoft.Json.Formatting.None);
                return StepOutcome.Success();
            }
        }
'''
flow = flow[:body + 1] + branch + flow[body + 1:]
io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
print('MagentoFlow.AddToCartAsync now sends both')
