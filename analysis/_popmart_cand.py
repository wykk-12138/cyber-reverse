import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
lam = re.compile(r'<([A-Za-z0-9_]+)>b__(\d+)_(\d+)')
hits = []
for ln in src:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if 'b__' not in t: continue
    found = lam.findall(t)
    if not found: continue
    ords = sorted(set(int(o) for _, o, _ in found))
    if any(115 <= o <= 135 for o in ords):
        hits.append((m.group(1), ords, [(n, int(o)) for n, o, _ in found]))
print('candidate tables overlapping 115..135:', len(hits))
for addr, ords, entries in hits[:14]:
    span = f'{ords[0]}..{ords[-1]}' if ords else '?'
    names = ', '.join(f'{o}:{n}' for n, o in entries[:8])
    print(f'{addr}  span={span:9s} n={len(entries):2d}  {names[:120]}')
