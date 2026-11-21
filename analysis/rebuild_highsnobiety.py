"""R1338d: rebuild the Highsnobiety block after my own anchor error destroyed RetailFlows.cs.

What went wrong: fix_action_variable.py sliced from the *first* `AddToCartAsync` in the file — which belongs to
another flow — to the discount doc-comment, and deleted every class in between. The file went from about 2500
lines to 235. Anchors in this file have to be scoped to a class, which is the same lesson as R1329's duplicate
check: a name that is unique in a class is not unique in a file holding dozens of them.

This restores the file from HEAD, then appends the whole corrected flow in one piece — with `$action` carrying
the line item, as the document requires — instead of patching it afterwards.

Usage: python analysis/rebuild_highsnobiety.py
"""
import io
import json
import subprocess

PATHS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

restored = subprocess.run(['git', 'show', 'HEAD:' + PATHS],
                          capture_output=True, check=True).stdout.decode('utf-8', 'replace')
print('restored %d lines from HEAD' % len(restored.splitlines()))

documents = json.loads(io.open('analysis/.highsnobiety_docs.json', encoding='utf-8').read())


def escape_literal(text):
    out = []
    for character in text:
        if character == '\\':
            out.append('\\\\')
        elif character == '"':
            out.append('\\"')
        elif character == '\r':
            out.append('\\r')
        elif character == '\n':
            out.append('\\n')
        elif character == '\t':
            out.append('\\t')
        else:
            out.append(character)
    return ''.join(out)


line_item = escape_literal(documents['add_line_item'])
discount = escape_literal(documents['add_discount_code'])

flow = '''
/// <summary>
/// Highsnobiety — a store the image supports and the replica had nowhere (R1337 found it by reading senders).
///
/// <para>
/// <b>Observed:</b> the add-to-cart and discount senders at <c>sub_140B56880</c> and <c>sub_140B585B0</c> post to
/// <c>https://tm-api-eu.highsnobiety.com/</c> (0x147089690, 35 characters) with <c>operationName</c>
/// <c>addLineItem</c> (0x146F6E208) and <c>addDiscountCode</c> (0x146F6E168), an <c>application/json</c>
/// envelope carrying <c>query</c> and <c>variables</c>, and the documents at 0x1470E6CDC (3435 characters) and
/// 0x1470E5234 (3399), both stored here with their CRLF line endings spelled out.
/// </para>
///
/// <para>
/// <b>Observed:</b> the add-to-cart document declares and uses exactly three variables — <c>$country</c>,
/// <c>$action</c> and <c>$locale</c> — and its operation is <c>addLineItem(country:, action:)</c>. There is no
/// sku argument: the line item travels inside <c>$action</c>, whose type <c>AddCartLineItem!</c> is an input
/// object the image never spells out.
/// </para>
///
/// <para>
/// <b>Unknown:</b> that input's field names. So the caller supplies <c>highsnobiety.action</c> as JSON and the
/// step passes it through; without it the step says what to set rather than sending a request built on a guess.
/// </para>
/// </summary>
public sealed class HighsnobietyFlow : StoreFlow
{
    /// <summary>The store's identifier.</summary>
    public override string Id => "highsnobiety";

    /// <summary>The store's display name.</summary>
    public override string Name => "Highsnobiety";

    /// <summary>The customer-facing domain. The API is on <see cref="ApiHost"/>, a different host.</summary>
    public override IReadOnlyList<string> Domains => new[] { "highsnobiety.com" };

    /// <summary>The API origin both senders compose, 0x147089690.</summary>
    public const string ApiHost = "https://tm-api-eu.highsnobiety.com/";

    /// <summary>The add-to-cart operation name, 0x146F6E208.</summary>
    public const string AddLineItemOperation = "addLineItem";

    /// <summary>The discount operation name, 0x146F6E168.</summary>
    public const string AddDiscountCodeOperation = "addDiscountCode";

    /// <summary>The add-to-cart document, 3435 characters from 0x1470E6CDC, CRLF included.</summary>
    public const string AddLineItemDocument =
        "__LINE_ITEM__";

    /// <summary>The discount document, 3399 characters from 0x1470E5234, CRLF included.</summary>
    public const string AddDiscountCodeDocument =
        "__DISCOUNT__";

    /// <summary>
    /// The three variable keys the document declares and uses. No <c>sku</c>: the operation is
    /// <c>addLineItem(country: $country, action: $action)</c>, so the line item is inside <c>$action</c>.
    /// </summary>
    public static readonly string[] AddLineItemVariables = { "action", "country", "locale" };

    /// <summary>
    /// Add the product to the cart. <c>highsnobiety.action</c> must hold the <c>AddCartLineItem</c> input as
    /// JSON; the image does not name its fields, so there is nothing to default to.
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var action = c.Session.Vars.GetValueOrDefault("highsnobiety.action");
        if (string.IsNullOrWhiteSpace(action))
            return StepOutcome.Fail("highsnobiety: $action is an AddCartLineItem input the image does not spell " +
                                    "out — set highsnobiety.action to its JSON before adding to cart");

        Newtonsoft.Json.Linq.JToken actionToken;
        try
        {
            actionToken = Newtonsoft.Json.Linq.JToken.Parse(action);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return StepOutcome.Fail("highsnobiety: highsnobiety.action is not valid JSON");
        }

        var country = c.Session.Vars.GetValueOrDefault("highsnobiety.country")
                      ?? c.ProfileData?.Country
                      ?? c.Session.Vars.GetValueOrDefault("country");
        if (string.IsNullOrEmpty(country)) return StepOutcome.Fail("highsnobiety: no country for $country!");

        var body = new JObject
        {
            ["operationName"] = AddLineItemOperation,
            ["query"] = AddLineItemDocument,
            ["variables"] = new JObject
            {
                ["action"] = actionToken,
                ["country"] = country,
                ["locale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.locale") ?? "en",
            },
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-add-line", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety add failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety add HTTP {res.StatusCode}", retryable: true);
        if (res.Body.Contains("\\"errors\\"", StringComparison.Ordinal))
            return StepOutcome.Fail("highsnobiety add: graphql returned errors");

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>Apply a discount code through the observed operation and its two variables.</summary>
    public async Task<StepOutcome> AddDiscountCodeAsync(FlowContext c, string code, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(code)) return StepOutcome.Fail("highsnobiety: no code");

        var body = new JObject
        {
            ["operationName"] = AddDiscountCodeOperation,
            ["query"] = AddDiscountCodeDocument,
            ["variables"] = new JObject
            {
                ["code"] = code,
                ["locale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.locale") ?? "en",
            },
        };

        var host = c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;
        var res = await PostJsonAsync(c, host, body.ToString(Newtonsoft.Json.Formatting.None),
            "hs-discount", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety discount failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety discount HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["discount"] = res.Body;
        return StepOutcome.Success();
    }
}
'''.replace('__LINE_ITEM__', line_item).replace('__DISCOUNT__', discount)

io.open(PATHS, 'w', encoding='utf-8', newline='').write(restored.rstrip() + '\n' + flow)
print('appended the corrected HighsnobietyFlow')
