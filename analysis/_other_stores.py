import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
def show(needle, limit=8):
    hits = sorted({r for r in rows if needle in r and '/v' in r})
    print('== %-24s %d' % (needle, len(hits)))
    for h in hits[:limit]: print('    ', h[:120])
show('farfetch.com/api')
show('magento')
show('preorder')
