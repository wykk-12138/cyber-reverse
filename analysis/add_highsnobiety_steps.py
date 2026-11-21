"""R1339: Highsnobiety gets two more steps — find product and submit email — with their documents.

The store's API host appears in eight code sites and those eight functions are its whole HTTP surface. Two of
them this round:

  fetchProduct      query fetchProduct($slug: String!, $locale: Locale!, $country: ...)   5718 chars at 0x1471407C4
                    variables slug / locale / preferredLocale / fallbackLocale / country
  setCustomerEmail  mutation setCustomerEmail($action: SetCartCustomerEmail!, $locale: ...) 4986 chars at 0x1470F8234
                    variables action / locale / preferredLocale

The types answer the question R1338 opened: `action` is an input object *per operation* — AddCartLineItem for the
cart line, SetCartCustomerEmail for the email — not one shared enum. So each step takes its own action JSON.

The class is regenerated whole from this script rather than patched: last round a slicing patch took RetailFlows
from 2066 lines to 235, and the fix is to never slice a file with dozens of classes in it.

Usage: python analysis/add_highsnobiety_steps.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

DOCS = 'analysis/.highsnobiety_docs.json'
PATHS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

SITES = {
    'add_line_item': 0x1470E6CDC,
    'add_discount_code': 0x1470E5234,
    'fetch_product': 0x1471407C4,
    'set_customer_email': 0x1470F8234,
}


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        reply = json.loads(reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


documents = {}
for name, address in SITES.items():
    documents[name] = read_string(address)
    print('%-20s %5d chars' % (name, len(documents[name])))

with io.open(DOCS, 'w', encoding='utf-8', newline='') as handle:
    json.dump(documents, handle, ensure_ascii=False, indent=1, sort_keys=True)


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


class_text = '''/// <summary>
/// Highsnobiety — a store the image supports and the replica had nowhere (R1337 found it by reading senders).
///
/// <para>
/// <b>Observed:</b> the API host <c>https://tm-api-eu.highsnobiety.com/</c> (0x147089690) appears in eight code
/// sites, and those eight functions are the store's whole HTTP surface. Each posts an
/// <c>application/json</c> envelope of <c>operationName</c>, <c>query</c> and <c>variables</c>:
/// <c>addLineItem</c> (0x140B56880), <c>createCheckoutPayment</c> (0x140B56CC0), <c>fetchProduct</c>
/// (0x140B57020), <c>fetchOrderConfirmation</c> (0x140B574F0), a billing sender (0x140B57EB0),
/// <c>addDiscountCode</c> (0x140B585B0), <c>setCustomerEmail</c> (0x140B58920) and a shipping sender
/// (0x140B59790).
/// </para>
///
/// <para>
/// <b>Observed:</b> <c>action</c> is an input object per operation, not one shared enum — the cart line takes
/// <c>AddCartLineItem</c> and the email takes <c>SetCartCustomerEmail</c>. Each step therefore takes its own
/// action JSON from the session, and the image never names either object's fields.
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

    /// <summary>The API origin every sender composes, 0x147089690.</summary>
    public const string ApiHost = "https://tm-api-eu.highsnobiety.com/";

    /// <summary>The add-to-cart operation name, 0x146F6E208.</summary>
    public const string AddLineItemOperation = "addLineItem";

    /// <summary>The discount operation name, 0x146F6E168.</summary>
    public const string AddDiscountCodeOperation = "addDiscountCode";

    /// <summary>The product query's operation name, 0x147033BA8.</summary>
    public const string FetchProductOperation = "fetchProduct";

    /// <summary>The email mutation's operation name, 0x147158FF0.</summary>
    public const string SetCustomerEmailOperation = "setCustomerEmail";

    /// <summary>The add-to-cart document, 3435 characters from 0x1470E6CDC, CRLF included.</summary>
    public const string AddLineItemDocument =
        "__ADD_LINE_ITEM__";

    /// <summary>The discount document, 3399 characters from 0x1470E5234.</summary>
    public const string AddDiscountCodeDocument =
        "__ADD_DISCOUNT__";

    /// <summary>The product query, 5718 characters from 0x1471407C4.</summary>
    public const string FetchProductDocument =
        "__FETCH_PRODUCT__";

    /// <summary>The email mutation, 4986 characters from 0x1470F8234.</summary>
    public const string SetCustomerEmailDocument =
        "__SET_EMAIL__";

    /// <summary>The three variable keys the add-to-cart document declares.</summary>
    public static readonly string[] AddLineItemVariables = { "action", "country", "locale" };

    /// <summary>The five variable keys the product query declares.</summary>
    public static readonly string[] FetchProductVariables = { "slug", "locale", "preferredLocale", "fallbackLocale", "country" };

    /// <summary>The three variable keys the email mutation declares.</summary>
    public static readonly string[] SetCustomerEmailVariables = { "action", "locale", "preferredLocale" };

    private JObject? ActionFrom(FlowContext c, string key, string step, out StepOutcome? failure)
    {
        failure = null;
        var raw = c.Session.Vars.GetValueOrDefault(key);
        if (string.IsNullOrWhiteSpace(raw))
        {
            failure = StepOutcome.Fail("highsnobiety: " + step + " takes an input object the image does not " +
                                       "spell out — set " + key + " to its JSON");
            return null;
        }

        try
        {
            return Newtonsoft.Json.Linq.JObject.Parse(raw);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            failure = StepOutcome.Fail("highsnobiety: " + key + " is not valid JSON");
            return null;
        }
    }

    private string Locale(FlowContext c) => c.Session.Vars.GetValueOrDefault("highsnobiety.locale") ?? "en";

    private string ApiHostFor(FlowContext c) =>
        c.Session.Vars.GetValueOrDefault("highsnobiety.apiHost") ?? ApiHost;

    private async Task<StepOutcome> PostOperationAsync(
        FlowContext c, string operation, string document, JObject variables, string label, string sessionKey,
        CancellationToken ct)
    {
        var body = new JObject
        {
            ["operationName"] = operation,
            ["query"] = document,
            ["variables"] = variables,
        };

        var res = await PostJsonAsync(c, ApiHostFor(c), body.ToString(Newtonsoft.Json.Formatting.None),
            label, ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("highsnobiety " + label + " failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"highsnobiety {label} HTTP {res.StatusCode}", retryable: true);
        if (res.Body.Contains("\\"errors\\"", StringComparison.Ordinal))
            return StepOutcome.Fail("highsnobiety " + label + ": graphql returned errors");

        c.Session.Vars[sessionKey] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Find the product by its slug. The document declares slug, locale, preferredLocale, fallbackLocale and
    /// country; the slug comes from the run, the others from the session with "en" as the locale default.
    /// </summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var slug = c.Session.Vars.GetValueOrDefault("slug") ?? c.Session.Vars.GetValueOrDefault("productSlug");
        if (string.IsNullOrEmpty(slug)) return StepOutcome.Fail("highsnobiety: no slug to look up");

        var country = c.Session.Vars.GetValueOrDefault("highsnobiety.country")
                      ?? c.ProfileData?.Country
                      ?? c.Session.Vars.GetValueOrDefault("country");
        if (string.IsNullOrEmpty(country)) return StepOutcome.Fail("highsnobiety: no country for $country!");

        var locale = Locale(c);
        var variables = new JObject
        {
            ["slug"] = slug,
            ["locale"] = locale,
            ["preferredLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.preferredLocale") ?? locale,
            ["fallbackLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.fallbackLocale") ?? locale,
            ["country"] = country,
        };

        return await PostOperationAsync(c, FetchProductOperation, FetchProductDocument, variables,
            "hs-product", "product", ct).ConfigureAwait(false);
    }

    /// <summary>Add the product to the cart; the line item is the caller's AddCartLineItem object.</summary>
    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        var action = ActionFrom(c, "highsnobiety.action", "add to cart", out var failure);
        if (action is null) return failure!.Value;

        var country = c.Session.Vars.GetValueOrDefault("highsnobiety.country")
                      ?? c.ProfileData?.Country
                      ?? c.Session.Vars.GetValueOrDefault("country");
        if (string.IsNullOrEmpty(country)) return StepOutcome.Fail("highsnobiety: no country for $country!");

        var variables = new JObject
        {
            ["action"] = action,
            ["country"] = country,
            ["locale"] = Locale(c),
        };

        return await PostOperationAsync(c, AddLineItemOperation, AddLineItemDocument, variables,
            "hs-add-line", "cart", ct).ConfigureAwait(false);
    }

    /// <summary>Set the cart's customer email; the payload is the caller's SetCartCustomerEmail object.</summary>
    public override async Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct)
    {
        var action = ActionFrom(c, "highsnobiety.emailAction", "submit email", out var failure);
        if (action is null) return failure!.Value;

        var variables = new JObject
        {
            ["action"] = action,
            ["locale"] = Locale(c),
            ["preferredLocale"] = c.Session.Vars.GetValueOrDefault("highsnobiety.preferredLocale") ?? Locale(c),
        };

        return await PostOperationAsync(c, SetCustomerEmailOperation, SetCustomerEmailDocument, variables,
            "hs-email", "email", ct).ConfigureAwait(false);
    }

    /// <summary>Apply a discount code through the observed operation and its two variables.</summary>
    public async Task<StepOutcome> AddDiscountCodeAsync(FlowContext c, string code, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(code)) return StepOutcome.Fail("highsnobiety: no code");

        var variables = new JObject
        {
            ["code"] = code,
            ["locale"] = Locale(c),
        };

        return await PostOperationAsync(c, AddDiscountCodeOperation, AddDiscountCodeDocument, variables,
            "hs-discount", "discount", ct).ConfigureAwait(false);
    }
}
'''.replace('__ADD_LINE_ITEM__', escape_literal(documents['add_line_item'])) \
   .replace('__ADD_DISCOUNT__', escape_literal(documents['add_discount_code'])) \
   .replace('__FETCH_PRODUCT__', escape_literal(documents['fetch_product'])) \
   .replace('__SET_EMAIL__', escape_literal(documents['set_customer_email']))

source = io.open(PATHS, encoding='utf-8', newline='').read()
marker = '/// <summary>\n/// Highsnobiety — a store the image supports and the replica had nowhere (R1337 found it by reading senders).'
start = source.find(marker)
if start < 0:
    raise SystemExit('the Highsnobiety block was not found')

io.open(PATHS, 'w', encoding='utf-8', newline='').write(source[:start].rstrip() + '\n\n' + class_text)
print('regenerated the class with four documents')
