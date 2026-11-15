import io, re, glob
params = {}
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'[?&]([a-zA-Z_][a-zA-Z0-9_]{1,24})=', t):
        params.setdefault(m.group(1), set()).add(f.split('replica\\')[-1].replace('\\','/'))
print('replica query params:', len(params))
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
pool = set(rows)
blob = '\n'.join(rows)
hit, miss = [], []
for name in sorted(params):
    if name in pool or (name + '=') in blob:
        hit.append(name)
    else:
        miss.append(name)
print('in pool: %d   not: %d' % (len(hit), len(miss)))
for name in miss:
    print('   %-24s %s' % (name, sorted(params[name])[0]))
