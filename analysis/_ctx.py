import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
targets = [0x07100354, 0x03376901, 0x0715aa44]
rows = []
for ln in lines:
    m = pat.match(ln)
    if not m: continue
    rows.append((int(m.group(1),16), m.group(2)))
for t in targets:
    print('=====', hex(t))
    idx = [i for i,a in enumerate(rows) if a[0]==t]
    if not idx: print('  not found'); continue
    i = idx[0]
    for j in range(max(0,i-3), min(len(rows), i+4)):
        mark = '>>' if j==i else '  '
        print(f'  {mark} {hex(rows[j][0])} {rows[j][1][:140]}')
