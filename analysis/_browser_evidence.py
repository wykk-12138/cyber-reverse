import io, re
pool = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in pool) if m]
print('pool lines:', len(rows))
def show(label, rx, limit=10):
    print('==', label)
    n = 0
    for a, t in rows:
        if re.search(rx, t):
            print('  ', a, t[:150])
            n += 1
            if n >= limit: break
    if n == 0: print('   (none)')
show('Browser.* locale keys', r'"Browser\.')
show('Splash', r'Splash', 8)
show('Window title-ish', r'"(Login|Splash|Browser)[A-Za-z.]*"', 8)
