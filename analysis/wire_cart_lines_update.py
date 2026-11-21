"""R1331: give the last orphan document a caller — cartLinesUpdate on the Storefront endpoint.

ShopifyGraphQl.CartLinesUpdate has been declared since the cart work and nothing sent it, while EditLineAsync
posts the REST /cart/update.js. The observed mutation is the structured form of the same act:

    mutation { cartLinesUpdate(cartId: $cartId, lines: $lines) { cart { checkoutUrl, lines(first:250){…} } } }

and it needs two things the flow already has when it reads the cart through GraphQL: the cart id and the
storefront token. What it also needs is the *line* id, which the cart read already receives
(lines.nodes[].id) and did not keep — so the read now remembers the first line id, and the edit uses it.

When any of the three is missing the REST call stays exactly as it was: this adds a path, it does not replace a
working one.

Usage: python analysis/wire_cart_lines_update.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'CartLinesUpdate' in text:
    raise SystemExit('already wired')

# 1) Remember the first line id after a successful cart read.
old_read_tail = '''        var checkoutUrl = ShopifyGraphQl.ParseCheckoutUrl(res.Body);
        if (checkoutUrl is not null) c.Session.Vars["checkoutUrl"] = checkoutUrl;

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();'''
new_read_tail = '''        var checkoutUrl = ShopifyGraphQl.ParseCheckoutUrl(res.Body);
        if (checkoutUrl is not null) c.Session.Vars["checkoutUrl"] = checkoutUrl;

        // R1331: cartLinesUpdate is keyed by line id, and the read already receives it (lines.nodes[].id) —
        // keeping it is what lets the edit take the structured path instead of the REST one.
        try
        {
            var lineId = JObject.Parse(res.Body)?["data"]?["cart"]?["lines"]?["nodes"] is JArray nodes && nodes.Count > 0
                ? nodes[0]?["id"]?.ToString()
                : null;
            if (!string.IsNullOrEmpty(lineId)) c.Session.Vars["shopify.lineId"] = lineId!;
        }
        catch (Newtonsoft.Json.JsonException)
        {
            // A reply that is not the shape we expect just means no line id; the REST edit still works.
        }

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();'''

if text.count(old_read_tail) != 1:
    raise SystemExit('cart read tail found %d times' % text.count(old_read_tail))
text = text.replace(old_read_tail, new_read_tail)

# 2) Edit the line through the observed mutation when the three keys are present.
old_edit = '''    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Quantity <= 1) return StepOutcome.Success();

        var payload = new JObject { ["line"] = 1, ["quantity"] = c.Session.Quantity };'''
new_edit = '''    public override async Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Quantity <= 1) return StepOutcome.Success();

        // R1331: the observed cartLinesUpdate mutation, when the read has supplied a cart id, a line id and a
        // storefront token. The REST call below is what this step did before and still does without them.
        var token = c.Session.Vars.GetValueOrDefault(GraphQlTokenVar);
        var graphQlCart = c.Session.Vars.GetValueOrDefault(GraphQlCartVar);
        var lineId = c.Session.Vars.GetValueOrDefault("shopify.lineId");
        if (!string.IsNullOrEmpty(token) && !string.IsNullOrEmpty(graphQlCart) && !string.IsNullOrEmpty(lineId))
        {
            var editPayload = new JObject
            {
                ["query"] = ShopifyGraphQl.CartLinesUpdate,
                ["variables"] = new JObject
                {
                    ["cartId"] = graphQlCart,
                    ["lines"] = new JArray { new JObject { ["id"] = lineId, ["quantity"] = c.Session.Quantity } },
                },
            };

            var editUrl = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
                c.Session.Vars.TryGetValue("shopify.apiVersion", out var editVersion) &&
                !string.IsNullOrWhiteSpace(editVersion) ? editVersion : "2025-04");

            c.Session.Headers[ShopifyHeaders.StorefrontAccessToken] = token;
            var edited = await PostJsonAsync(c, editUrl,
                editPayload.ToString(Newtonsoft.Json.Formatting.None), "shopify-cart-lines", ct)
                .ConfigureAwait(false);

            if (edited is { IsSuccess: true })
            {
                c.Session.Vars["cart"] = edited.Body;
                return StepOutcome.Success();
            }

            return StepOutcome.Fail($"shopify cart line update HTTP {edited?.StatusCode}", retryable: true);
        }

        var payload = new JObject { ["line"] = 1, ["quantity"] = c.Session.Quantity };'''

if text.count(old_edit) != 1:
    raise SystemExit('edit site found %d times' % text.count(old_edit))
text = text.replace(old_edit, new_edit)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('wired cartLinesUpdate into EditLineAsync and the line id into the cart read')
