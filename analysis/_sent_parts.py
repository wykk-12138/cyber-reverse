import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
paths = [r for r in rows if r.startswith('/') or '/rest/' in r or '/web-api/' in r]

targets = ['/account/recover','/account/verify','/api/checkout/v1/basket','/api/preorder/entry','/api/stock',
           '/collections/new-releases','/rest/V1/carts/mine/totals','/v1/buys']
for t in targets:
    segs = [s for s in t.split('/') if s]
    key = segs[-1]
    hits = [r for r in rows if key in r][:3]
    print('== %-34s 末段 %-14s 池中相关 %d' % (t, key, len([r for r in rows if key in r])))
    for h in hits: print('      ', h[:95])
