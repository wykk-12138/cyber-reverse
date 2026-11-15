import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = []
for ln in lines:
    m = pat.match(ln)
    if m: rows.append((int(m.group(1),16), m.group(2)))
hits = [(a,t) for a,t in rows if t.startswith('shopify-') or t.startswith('X-Shopify') or t.startswith('x-shopify')]
for a,t in hits:
    print(hex(a), t[:100])
print('---- total', len(hits))
