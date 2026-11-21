"""R1338: Highsnobiety becomes a store — the first flow built entirely from a sender read.

R1337 found the store by reading the sender of two documents: https://tm-api-eu.highsnobiety.com/ with
operationName addLineItem and addDiscountCode, variables sku/locale/country/action and code/locale. This round
decodes both documents and turns them into a flow, which is priority ① (site checkout flows) and the first time
this project has built a store from an endpoint rather than from a page.

What the senders give, and what they do not:

  given      the host, the two operation names, the envelope keys, the variable names and their types
             ($country: Country!, $action: AddCartLineItem!, $locale: Locale, $sku: String!, $code: String!)
  not given  the value of `$action`. The literal near it is "Add to cart", which cannot be an enum value, so the
             step requires the caller to supply it and says so rather than guessing an enum member.

Usage: python analysis/add_highsnobiety_flow.py
"""
import io
import json

DOCS = 'analysis/.highsnobiety_docs.json'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
REGISTRY = 'replica/src/Cybersole.Stores/Modules/Registry.cs'

documents = json.loads(io.open(DOCS, encoding='utf-8').read())
line_item = documents['add_line_item'].replace('"', '""')
discount = documents['add_discount_code'].replace('"', '""')

flow = '''
/// <summary>
/// Highsnobiety — a store the image supports and the replica had nowhere.
///
/// <para>
/// <b>Observed</b> (R1337/R1338): the add-to-cart and discount senders at <c>sub_140B56880</c> and
/// <c>sub_140B585B0</c> post to <c>https://tm-api-eu.highsnobiety.com/</c> with <c>operationName</c>
/// <c>addLineItem</c> / <c>addDiscountCode</c>, an <c>application/json</c> envelope carrying <c>query</c> and
/// <c>variables</c>, and the documents at 0x1470E6CDC (3435 characters) and 0x1470E5234 (3399).
/// </para>
///
/// <para>
/// <b>Unknown:</b> the value of <c>$action</c>, whose document type is the enum <c>AddCartLineItem</c>. The only
/// literal near it in the sender is <c>"Add to cart"</c>, which cannot be an enum member, so the step asks the
/// caller for <c>highsnobiety.action</c> and reports its absence rather than inventing a value.
/// </para>
/// </summary>
public sealed class HighsnobietyFlow : StoreFlow
{
    /// <summary>The store's identifier, as the catalogue spells it.</summary>
    public override string Id => "highsnobiety";

    /// <summary>The store's display name.</summary>
    public override string Name => "Highsnobiety";

    /// <summary>The customer-facing domain. The API lives on <see cref="ApiHost"/>, a different host.</summary>
    public override IReadOnlyList<string> Domains => new[] { "highsnobiety.com" };

    /// <summary>The API origin both senders compose, 0x147089690 (35 characters, trailing slash included).</summary>
    public const string ApiHost = "https://tm-api-eu.highsnobiety.com/";

    /// <summary>The operation name the add-to-cart sender sets, 0x146F6E208.</summary>
    public const string AddLineItemOperation = "addLineItem";

    /// <summary>The operation name the discount sender sets, 0x146F6E168.</summary>
    public const string AddDiscountCodeOperation = "addDiscountCode";

    /// <summary>The add-to-cart document, 3435 characters from 0x1470E6CDC.</summary>
    public const string AddLineItemDocument = @"__LINE_ITEM__";

    /// <summary>The discount document, 3399 characters from 0x1470E5234.</summary>
    public const string AddDiscountCodeDocument = @"__DISCOUNT__";

    /// <summary>The four variable keys the add-to-cart sender fills, in the document's own names.</summary>
    public static readonly string[] AddLineItemVariables = { "sku", "action", "country", "locale" };

    /// <summary>
    /// Add the product to the cart. The action is required by the document's own type and its value is not in the
    /// image, so a run without <c>highsnobiety.action</c> is told that rather than sent with a guess.
    /// </summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var sku = c.Session.Vars.GetValueOrDefault("sku") ?? c.Session.Sku;
        if (string.IsNullOrEmpty(sku)) return StepOutcome.Fail("highsnobiety: no sku to add");

        var action = c.Session.Vars.GetValueOrDefault("highsnobiety.action");
        if (string.IsNullOrEmpty(action))
            return StepOutcome.Fail("highsnobiety: $action is an enum the image does not name — set " +
                                    "highsnobiety.action before adding to cart");

        var country = c.Session.Vars.GetValueOrDefault("highsnobiety.country")
                      ?? c.ProfileData?.Country
                      ?? c.Session.Vars.GetValueOrDefault("country");
        if (string.IsNullOrEmpty(country)) return StepOutcome.Fail("highsnobiety: no country for $country!");

        var variables = new JObject
        {
            ["sku"] = sku,
            ["action"] = action,
            ["country"] = country,
            ["locale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.locale") ?? "en",
        };

        var body = new JObject
        {
            ["operationName"] = AddLineItemOperation,
            ["query"] = AddLineItemDocument,
            ["variables"] = variables,
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

    /// <summary>
    /// Apply a discount code. Not a base step, so nothing calls it until a task does; the document and its two
    /// variables are the ones the image's sender uses.
    /// </summary>
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

text = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'class HighsnobietyFlow' in text:
    raise SystemExit('flow already present')

io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text.rstrip() + '\n' + flow)
print('appended HighsnobietyFlow (%d + %d document chars)' % (len(documents['add_line_item']),
                                                              len(documents['add_discount_code'])))

registry = io.open(REGISTRY, encoding='utf-8', newline='').read()
if 'HighsnobietyFlow' in registry:
    raise SystemExit('already registered')

anchor = '        new FlowStoreModule(new SuperswipeFlow()),'
if registry.count(anchor) != 1:
    raise SystemExit('registry anchor found %d times' % registry.count(anchor))

registry = registry.replace(
    anchor,
    '        // R1338: found by reading the senders of addLineItem and addDiscountCode — the API is on\n'
    '        // tm-api-eu.highsnobiety.com, not on the customer-facing domain.\n'
    '        new FlowStoreModule(new HighsnobietyFlow()),\n' + anchor)
io.open(REGISTRY, 'w', encoding='utf-8', newline='').write(registry)
print('registered HighsnobietyFlow')
