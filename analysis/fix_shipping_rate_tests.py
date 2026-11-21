"""Fix the two compile errors in the new shipping-rate tests: init-only ProfileData, and JToken.Value<T>()."""

import io

PATH = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

old_ctx = '''        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.ProfileData = new Cybersole.Core.Models.Profile
        {
            FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
            City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
        };'''
new_ctx = '''        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            ProfileData = new Cybersole.Core.Models.Profile
            {
                FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
                City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
            },
        };'''

count = text.count(old_ctx)
if count != 2:
    raise SystemExit('context blocks found %d times' % count)
text = text.replace(old_ctx, new_ctx)

for old, new in (
    ('rateRequest["variables"]!["selectedShippingRateId"]!.Value<int>()',
     'rateRequest["variables"]!["selectedShippingRateId"]!.ToObject<int>()'),
    ('rateRequest["variables"]!["isNewsletterSubscribed"]!.Value<bool>()',
     'rateRequest["variables"]!["isNewsletterSubscribed"]!.ToObject<bool>()'),
):
    if text.count(old) != 1:
        raise SystemExit('%s found %d times' % (old, text.count(old)))
    text = text.replace(old, new)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('fixed ProfileData initialisation and the JToken conversions')
