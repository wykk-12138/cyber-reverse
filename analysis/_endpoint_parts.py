import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
for needle in ('cart/add', '/api/cart', 'beast', 'checkout/submit', 'api/settings', 'api/beast'):
    hits = [t for t in rows if needle in t][:4]
    print('== %-18s %d' % (needle, len([t for t in rows if needle in t])))
    for h in hits: print('     ', h[:100])
