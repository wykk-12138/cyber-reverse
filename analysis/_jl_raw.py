import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]
hits = [(i, a, t) for i, (a, t) in enumerate(rows) if 'GetProductHtml' in t]
print('rows containing GetProductHtml:', len(hits))
for i, a, t in hits[:3]:
    print('  at 0x%x: %r' % (a, t[:90]))
    for j in range(max(0, i-2), min(len(rows), i+3)):
        print('     0x%x %r' % (rows[j][0], rows[j][1][:70]))
