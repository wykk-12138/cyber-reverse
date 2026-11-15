import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
# lambda literal tables look like  "<Name>b__NNN_M"
lam = re.compile(r'<([A-Za-z0-9_]+)>b__(\d+)_(\d+)')
rows = []
for ln in src:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if 'b__' not in t: continue
    found = lam.findall(t)
    if len(found) >= 3:
        rows.append((m.group(1), found))
print('lambda tables with >=3 entries:', len(rows))
for addr, found in rows[:12]:
    first = found[0][1]; last = found[-1][1]
    print(f'{addr}  entries={len(found):3d}  range={first}..{last}')
