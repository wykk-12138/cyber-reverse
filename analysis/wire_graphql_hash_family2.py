"""Hang the branch on GetCartAsync, which exists — ProcessCartAsync does not."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/GraphQlHashQueriesTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'GraphQlHashQueries' not in text:
    marker = 'public virtual Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('GetCartAsync not found')

    end = text.find(';', position)
    original = text[position:end + 1]
    replacement = '''public virtual async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        // R1357: the family that posts persisted queries by hash. When a run names an origin for it, the cart comes
        // from there; the hash is the run's because the image holds two and pairs neither with an operation.
        var hashOrigin = c.Session.Vars.GetValueOrDefault("graphqlHash.origin");
        if (!string.IsNullOrEmpty(hashOrigin))
        {
            var (hashData, hashError) = await GraphQlHashQueries
                .SendAsync(c, hashOrigin, "GetCart", new Newtonsoft.Json.Linq.JObject(),
                    c.Session.Vars.GetValueOrDefault("graphqlHash.cartHash"), ct)
                .ConfigureAwait(false);
            if (hashData is null) return StepOutcome.Fail(hashError);

            c.Session.Vars["cart"] = hashData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return await NotSupported("GetCart").ConfigureAwait(false);
    }'''
    text = text[:position] + replacement + text[end + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('GetCartAsync now consults the hash family (%d chars replaced)' % len(original))

if not io.open(TESTS, encoding='utf-8').read().startswith('using System.Threading.Tasks;'):
    raise SystemExit('tests missing')
print('tests already written')
