"""Point the structured-edit test at its local server through the new seam."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

old = 'ctx.Session.Vars["shopify.apiVersion"] = "2025-04";'
new = 'ctx.Session.Vars["shopify.graphqlBase"] = server.BaseUrl + "/graphql";'

if text.count(old) != 1:
    raise SystemExit('anchor found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('test now uses the seam')
