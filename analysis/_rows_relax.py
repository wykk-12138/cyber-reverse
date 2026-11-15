import io, re, json
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]
single = re.compile(r'^[^<]{0,3}<(\w+)>d__(\d+)$')

def groups(min_rows, gap):
    out, cur = [], []
    for addr, text in rows:
        m = single.match(text.strip())
        if m and cur and addr - cur[-1][0] <= gap:
            cur.append((addr, m.group(1), int(m.group(2))))
        elif m:
            if len(cur) >= min_rows: out.append(cur)
            cur = [(addr, m.group(1), int(m.group(2)))]
        else:
            if len(cur) >= min_rows: out.append(cur)
            cur = []
    if len(cur) >= min_rows: out.append(cur)
    return out

for min_rows, gap in ((3, 0x60), (2, 0x60), (2, 0xC0), (2, 0x180)):
    g = groups(min_rows, gap)
    print('min_rows=%d gap=0x%02x -> %d 段 / %d 步' % (min_rows, gap, len(g), sum(len(x) for x in g)))

g = groups(2, 0xC0)
g.sort(key=lambda x: x[0][0])
print()
print('地址顺序（前 20 段，含 John Lewis 的邻域）:')
for x in g[:20]:
    print('  0x%08x  %2d 步  %s%s' % (x[0][0], len(x), ', '.join(n for _, n, _ in x[:4]), ' …' if len(x) > 4 else ''))
io.open('row_groups_wide.json','w',encoding='utf-8').write(json.dumps(
    [{'base': '0x%x' % x[0][0], 'steps': [[o, n] for _, n, o in x]} for x in g], ensure_ascii=False, indent=1))
print('written row_groups_wide.json')
