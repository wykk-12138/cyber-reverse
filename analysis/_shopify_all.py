import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
for needle in ('X-Shopify-Generated-Cart-Token', 'X-Shopify-Storefront-Access-Token', 'Shopify'):
    hits = [(a, t) for a, t in rows if needle in t]
    print('==', needle, len(hits))
    for a, t in hits[:6]:
        print('   ', a, len(t), t[:100].replace('\n', ' '))
