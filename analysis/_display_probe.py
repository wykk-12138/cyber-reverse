import io, re, collections
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2) for m in (pat.match(l) for l in lines) if m]
blob_rows = rows

disp = collections.defaultdict(set)
for t in blob_rows:
    for m in re.finditer(r'<>c__DisplayClass(\d+)_(\d+)', t):
        disp[int(m.group(1))].add('DisplayClass' + m.group(1) + '_' + m.group(2))
    for m in re.finditer(r'<<(\w+)>b__(\d+)_(\d+)>', t):
        disp[int(m.group(2))].add('lambda ' + m.group(1))

print('ordinals with closures/lambdas:', len(disp))
for o in range(18, 32):
    names = sorted(disp.get(o, []))
    print('  %3d  %s' % (o, ', '.join(n[:40] for n in names[:4]) or '-'))
