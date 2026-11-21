"""R1337: retract R1334 — /cartApi/checkout is not where the Magento cart mutations go.

R1334 encoded a rule: compose https://<host www->themeapis>/cartApi/checkout for a bare host, and pass every
MagentoCart endpoint through it. The rule itself was read correctly, but R1334 attached it to the wrong family.
Reading the actual senders this round settles what goes where:

    SubmitOrder         https:// + host + /graphql   operationName SubmitOrder, variables, cartToken
    addLineItem         https://tm-api-eu.highsnobiety.com/   operationName addLineItem, sku/locale/country
    addDiscountCode     https://tm-api-eu.highsnobiety.com/   operationName addDiscountCode, code/locale
    cartApiObjectCreate api/2025-04/graphql.json (Shopify Storefront), gid://shopify/ProductVariant/,
                        customerAccessToken, includeCustomerTags, includeSellingPlans, includeStoreAvailability
    createEmptyCart     no URL literal at all — the endpoint is the caller's

And /cartApi/checkout's own sender works with cartType / lineItems / locationId / sourceSystem valued Retail
and Shopify — none of which any Magento cart mutation sends. So the two families are different, and R1334's
wiring put a path on documents that do not use it.

This removes the four members and their six call sites, and the five tests that pinned them. A rule that is
true of something else is worse than no rule: it looks like evidence and would misroute an endpoint the first
time a caller passed a bare host.

Usage: python analysis/retract_cartapi_endpoint.py
"""
import io
import re

SRC = 'replica/src/Cybersole.Stores/Flows/MagentoCart.cs'
TESTS = 'replica/tests/Cybersole.Tests/MagentoCartTests.cs'

text = io.open(SRC, encoding='utf-8', newline='').read()

start = text.find('    /// <summary>\n    /// The cart-API path the observed family posts to')
end_marker = '    public static string ResolveEndpoint(string endpointOrHost) =>\n' \
             '        endpointOrHost.Contains("://", StringComparison.Ordinal)\n' \
             '            ? endpointOrHost\n' \
             '            : CartApiEndpointFor(endpointOrHost);\n'
end = text.find(end_marker)
if start < 0 or end < 0:
    raise SystemExit('members not found (start=%s end=%s)' % (start, end))

text = text[:start] + text[end + len(end_marker):]

# Remove the ThemeApisHost helper too, wherever it sits inside the same region.
helper_start = text.find('    /// <summary>\n    /// The host the cart API lives on')
if helper_start >= 0:
    helper_end = text.find('\n    }\n', text.find('public static string ThemeApisHost')) + len('\n    }\n')
    text = text[:helper_start] + text[helper_end:]
    print('removed ThemeApisHost')

removed = text.count('        endpoint = ResolveEndpoint(endpoint);')
text = text.replace('\n        endpoint = ResolveEndpoint(endpoint);', '')
print('removed %d normalisation lines' % removed)

if 'ResolveEndpoint' in text or 'CartApiEndpointFor' in text or 'CartApiPath' in text:
    raise SystemExit('leftover reference to the retracted rule')

io.open(SRC, 'w', encoding='utf-8', newline='').write(text)

tests = io.open(TESTS, encoding='utf-8', newline='').read()
test_start = tests.find('    /// <summary>\n    /// R1334: the image composes the cart-API endpoint')
if test_start < 0:
    raise SystemExit('tests not found')
tests = tests[:test_start].rstrip('\n') + '\n}\n'
io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('removed the R1334 tests')
