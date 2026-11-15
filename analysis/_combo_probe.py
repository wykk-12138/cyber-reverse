import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
d_state = re.compile(r'<(\w+)>d__(\d+)')
lam = re.compile(r'<(\w+)>b__(\d+)_')
both = []
for a, t in rows:
    ds = d_state.findall(t)
    ls = lam.findall(t)
    if len(ds) >= 2 and ls:
        both.append((a, ds, ls, t))
print('literals with BOTH a d__ sequence and lambdas:', len(both))
for a, ds, ls, t in both[:6]:
    print('==', a, 'len', len(t))
    print('   d__ :', ', '.join('%s(%s)' % (n, o) for n, o in ds[:10]))
    print('   lam :', ', '.join('%s(%s)' % (n, o) for n, o in ls[:10]))
