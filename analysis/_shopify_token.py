import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
def show(rx, limit=8, before=1, after=3):
    print('=====', rx)
    n = 0
    for i, (a, t) in enumerate(rows):
        if re.search(rx, t):
            for j in range(max(0, i - before), min(len(rows), i + after + 1)):
                print(('>>' if j == i else '  '), rows[j][0], rows[j][1][:120])
            print('  ---')
            n += 1
            if n >= limit: break
    if n == 0: print('   (none)')
show(r'X-Shopify', 6, 1, 3)
