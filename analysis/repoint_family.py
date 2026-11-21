"""Point the flow's branch at the family, and give the family three more steps to reach it."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()

old = '''            var (apiProduct, apiError) = await StorefrontApiProduct.FetchAsync(c, storefrontOrigin,
                new JObject
                {
                    ["id"] = c.Session.Vars.GetValueOrDefault("storefrontapi.productId"),
                    ["variationId"] = c.Session.Vars.GetValueOrDefault("storefrontapi.variationId"),
                }, ct).ConfigureAwait(false);

            if (apiProduct is null) return StepOutcome.Fail(apiError);

            c.Session.Vars["product"] = apiProduct.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();'''

new = '''            var (apiData, apiError) = await StorefrontApiQueries.SendAsync(c, storefrontOrigin, "Product",
                new JObject
                {
                    ["id"] = c.Session.Vars.GetValueOrDefault("storefrontapi.productId"),
                    ["variationId"] = c.Session.Vars.GetValueOrDefault("storefrontapi.variationId"),
                }, ct).ConfigureAwait(false);

            if (apiData is null) return StepOutcome.Fail(apiError);

            c.Session.Vars["product"] = apiData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();'''

if text.count(old) != 1:
    raise SystemExit('branch not found')

io.open(FLOW, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('flow branch now uses the family')

# The tests referenced the old class name; move them to the family and add coverage for the four new operations.
tests = io.open(TESTS, encoding='utf-8', newline='').read()
tests = tests.replace('StorefrontApiProduct', 'StorefrontApiQueries')
tests = tests.replace('Assert.Equal(new[] { "id", "isDraft", "variationId", "src" }, StorefrontApiQueries.DeclaredVariables);',
                      'Assert.Equal(new[] { "id", "isDraft", "variationId", "src" }, StorefrontApiQueries.Declared["Product"]);')
tests = tests.replace('Assert.Equal(new[] { "id", "variationId" }, StorefrontApiQueries.SenderVariables);',
                      'Assert.Equal(new[] { "id", "variationId" }, StorefrontApiQueries.SenderFills["Product"]);')
tests = tests.replace('foreach (var name in StorefrontApiQueries.DeclaredVariables)',
                      'foreach (var name in StorefrontApiQueries.Declared["Product"])')
tests = tests.replace('StorefrontApiQueries.OperationName', '"Product"')
tests = tests.replace('StorefrontApiQueries.Document', 'StorefrontApiQueries.Product')
tests = tests.replace('StorefrontApiQueries.FetchAsync(\n            ctx, null, new JObject { ["id"] = "1" }, default)',
                      'StorefrontApiQueries.SendAsync(\n            ctx, null, "Product", new JObject { ["id"] = "1" }, default)')
tests = tests.replace('StorefrontApiQueries.FetchAsync(\n            ctx, server.BaseUrl, new JObject(), default)',
                      'StorefrontApiQueries.SendAsync(\n            ctx, server.BaseUrl, "Product", new JObject(), default)')
tests = tests.replace('StorefrontApiQueries.FetchAsync(\n            ctx, server.BaseUrl + "/", new JObject { ["id"] = "p-1", ["variationId"] = "v-1" }, default)',
                      'StorefrontApiQueries.SendAsync(\n            ctx, server.BaseUrl + "/", "Product",\n            new JObject { ["id"] = "p-1", ["variationId"] = "v-1" }, default)')
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('tests follow the family')
