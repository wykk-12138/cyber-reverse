"""R1338c: `action` is an input object, not a sibling variable — the document says so.

The document declares and uses exactly three variables: $country, $action and $locale. Its operation is
addLineItem(country: $country, action: $action) and there is no sku argument anywhere. So `$action` carries the
line item, which means its type `AddCartLineItem!` is an input object and the sku lives inside it.

My first version sent sku as a fourth top-level variable, which the document would have rejected. This corrects
that: the caller supplies the action object (its field names are not in the image), and the step passes it
through untouched and says what is missing when it is absent.

Usage: python analysis/fix_action_variable.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
TESTS = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'

text = io.open(PATH, encoding='utf-8', newline='').read()

old_doc = '''    /// <summary>The four variable keys the add-to-cart sender fills, in the document's own names.</summary>
    public static readonly string[] AddLineItemVariables = { "sku", "action", "country", "locale" };'''
new_doc = '''    /// <summary>
    /// The three variable keys the document declares and uses. There is no <c>sku</c> among them — the operation
    /// is <c>addLineItem(country: $country, action: $action)</c>, so the line item travels inside
    /// <c>$action</c>, whose type <c>AddCartLineItem!</c> is an input object whose fields the image does not name.
    /// </summary>
    public static readonly string[] AddLineItemVariables = { "action", "country", "locale" };'''

if text.count(old_doc) != 1:
    raise SystemExit('variable list not found')
text = text.replace(old_doc, new_doc)

start = text.find('    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)')
end = text.find('    /// <summary>\n    /// Apply a discount code.', start)
if start < 0 or end < 0:
    raise SystemExit('AddToCartAsync body not found')

replacement = '''    public override async Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct)
    {
        // The line item is not a variable of its own: the document is addLineItem(country:, action:) and the sku
        // travels inside $action, an AddCartLineItem the image never spells out. The caller supplies that object.
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

        var variables = new JObject
        {
            ["action"] = actionToken,
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

'''

text = text[:start] + replacement + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('AddToCartAsync now carries the action object')

tests = io.open(TESTS, encoding='utf-8', newline='').read()
tests = tests.replace(
    '        Assert.Equal(new[] { "sku", "action", "country", "locale" }, HighsnobietyFlow.AddLineItemVariables);',
    '        Assert.Equal(new[] { "action", "country", "locale" }, HighsnobietyFlow.AddLineItemVariables);')
tests = tests.replace(
    '        ctx.Session.Vars["sku"] = "HS-1";\n        ctx.Session.Vars["highsnobiety.action"] = "ADD";',
    '        ctx.Session.Vars["highsnobiety.action"] = "{\\"sku\\":\\"HS-1\\",\\"quantity\\":1}";')
tests = tests.replace(
    '''        Assert.Equal("HS-1", sent["variables"]!["sku"]!.ToObject<string>());
        Assert.Equal("ADD", sent["variables"]!["action"]!.ToObject<string>());''',
    '''        Assert.Equal("HS-1", sent["variables"]!["action"]!["sku"]!.ToObject<string>());
        Assert.Equal(1, sent["variables"]!["action"]!["quantity"]!.ToObject<int>());
        Assert.Null(sent["variables"]!["sku"]);''')
tests = tests.replace('        ctx.Session.Vars["sku"] = "HS-1";\n\n        var outcome = await new HighsnobietyFlow().AddToCartAsync',
                      '\n        var outcome = await new HighsnobietyFlow().AddToCartAsync')
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('tests follow the corrected shape')
