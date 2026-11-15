import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]

targets = ['/account/recover','/account/verify','/api/basket/v1/items','/api/beast','/api/checkout/submit',
 '/api/checkout/v1/basket/{basketId}','/api/checkout/v1/basket/{basketId}/place-order',
 '/api/checkout/v1/basket/{basketId}/shipping','/api/order/submit','/api/preorder/entry','/api/search',
 '/api/stock','/api/v1/carts/{c.Session.CartId}','/api/v1/carts/{c.Session.CartId}/items',
 '/api/v2/shop/countries','/collections/new-releases','/rest/V1/carts/mine/totals','/v1/buys',
 '/v1/buys/{c.Session.CartId}','/view/resources/getUserInfo','/v1/carts/{c.Session.CartId}/items']
found, missing = [], []
for t in targets:
    # strip template placeholders, search the literal prefix
    stem = re.split(r'\{', t)[0].rstrip('/')
    hits = [r for r in rows if stem and stem in r]
    if hits:
        found.append((t, hits[0][:100]))
    else:
        missing.append(t)
print('有证据(整条或作为 URL 的一部分): %d' % len(found))
for t, h in found: print('  %-46s <- %s' % (t, h))
print()
print('仍无证据: %d' % len(missing))
for t in missing: print('  ', t)
