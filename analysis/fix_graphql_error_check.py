"""R1330b: "errors" in the reply is not the same as "errors happened".

The Warhammer steps decided failure with `res.Body.Contains("\\"errors\\"")`. That is wrong twice over: the
observed mutations return an `errors` field as part of their payload (`updateShippingRate { errors order {…} }`,
`updateShippingAddress { errors … }`), so a *successful* answer contains the word; and an empty array — the
successful case — is still the word. Every rate response would have been reported as a failure, which is how the
new shipping-rate test found it.

The check becomes structural: parse the body, and treat it as failed only when there is a non-empty `errors`
array, either at the top level or inside the operation's payload.

Usage: python analysis/fix_graphql_error_check.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'HasGraphQlErrors' in text:
    raise SystemExit('helper already present')

helper = (
    '    /// <summary>\n'
    '    /// True when a GraphQL reply reports errors. R1330: the steps used to ask whether the body *contains*\n'
    '    /// the word "errors", which is true of every successful answer too — the observed mutations return an\n'
    '    /// <c>errors</c> field as part of their payload, and an empty array is the good case. This checks for a\n'
    '    /// non-empty array, at the top level or inside the operation.\n'
    '    /// </summary>\n'
    '    private static bool HasGraphQlErrors(string body)\n'
    '    {\n'
    '        try\n'
    '        {\n'
    '            var root = Newtonsoft.Json.Linq.JObject.Parse(body);\n'
    '            if (root["errors"] is Newtonsoft.Json.Linq.JArray top && top.Count > 0) return true;\n'
    '            if (root["data"] is not Newtonsoft.Json.Linq.JObject data) return false;\n'
    '\n'
    '            foreach (var operation in data.Properties())\n'
    '                if (operation.Value is Newtonsoft.Json.Linq.JObject payload &&\n'
    '                    payload["errors"] is Newtonsoft.Json.Linq.JArray errors && errors.Count > 0)\n'
    '                    return true;\n'
    '\n'
    '            return false;\n'
    '        }\n'
    '        catch (Newtonsoft.Json.JsonException)\n'
    '        {\n'
    '            // An unparseable body cannot be claimed as success.\n'
    '            return true;\n'
    '        }\n'
    '    }\n'
    '\n'
)

anchor = '    public override async Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct)'
if text.count(anchor) != 1:
    raise SystemExit('shipping anchor found %d times' % text.count(anchor))
text = text.replace(anchor, helper + anchor)

# Replace the three naive checks in this class.
old_check = '''        if (res.IsSuccess && res.Body.Contains("\\"errors\\"", StringComparison.Ordinal))'''
new_check = '''        if (res.IsSuccess && HasGraphQlErrors(res.Body))'''
count = text.count(old_check)
print('naive res checks: %d' % count)
text = text.replace(old_check, new_check)

for variable in ('rated', 'onboarded'):
    old = '        if (%s.IsSuccess && %s.Body.Contains("\\"errors\\"", StringComparison.Ordinal))' % (variable, variable)
    new = '        if (%s.IsSuccess && HasGraphQlErrors(%s.Body))' % (variable, variable)
    hits = text.count(old)
    print('%s checks: %d' % (variable, hits))
    text = text.replace(old, new)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('error checks are structural now')
