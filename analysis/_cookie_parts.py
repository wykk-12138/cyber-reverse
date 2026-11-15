import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for needle in ('NIKE_COMMERCE', 'commerce_country', 'ffid', 'sbsd', 'SBSD', '_abck', 'bm_sz'):
    hits = [t for t in rows if needle in t]
    print('== %-18s %d' % (needle, len(hits)))
    for h in hits[:3]: print('    ', h[:100])
