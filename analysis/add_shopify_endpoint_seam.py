"""R1331b: the Storefront endpoint is hard-coded to https, so nothing can intercept it.

ShopifyGraphQl.Endpoint builds https://{host}/api/{version}/graphql.json from the flow's own URL. A local test
server speaks http, so the structured edit could not be exercised at all — the request left for https://127.0.0.1
and failed on TLS. The fix is the same seam the other flows use: a session override that replaces the endpoint
outright, with the composed URL as the default.

Usage: python analysis/add_shopify_endpoint_seam.py
"""
import io

PATH = 'replica/src/Cybersole.Stores/Flows/ShopifyFlow.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

if 'shopify.graphqlBase' in text:
    raise SystemExit('seam already present')

old = '''            var editUrl = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
                c.Session.Vars.TryGetValue("shopify.apiVersion", out var editVersion) &&
                !string.IsNullOrWhiteSpace(editVersion) ? editVersion : "2025-04");'''
new = '''            // R1331: the composed endpoint is https, so a capture or a test cannot point it elsewhere. The
            // session override replaces it outright; the default is unchanged.
            var editUrl = c.Session.Vars.GetValueOrDefault("shopify.graphqlBase");
            if (string.IsNullOrEmpty(editUrl))
                editUrl = ShopifyGraphQl.Endpoint(new Uri(c.Url).Host,
                    c.Session.Vars.TryGetValue("shopify.apiVersion", out var editVersion) &&
                    !string.IsNullOrWhiteSpace(editVersion) ? editVersion : "2025-04");'''

if text.count(old) != 1:
    raise SystemExit('edit url site found %d times' % text.count(old))

io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
print('added the shopify.graphqlBase seam')
