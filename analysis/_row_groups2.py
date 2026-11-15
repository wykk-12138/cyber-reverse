import io, re, json
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]
single = re.compile(r'^[^<]{0,3}<(\w+)>d__(\d+)$')

groups, cur = [], []
for addr, text in rows:
    m = single.match(text.strip())
    if m and cur and addr - cur[-1][0] <= 0x60:
        cur.append((addr, m.group(1), int(m.group(2))))
    elif m:
        if len(cur) >= 3: groups.append(cur)
        cur = [(addr, m.group(1), int(m.group(2)))]
    else:
        if len(cur) >= 3: groups.append(cur)
        cur = []
if len(cur) >= 3: groups.append(cur)

print('groups (>=3 adjacent single-d__ rows):', len(groups))
print('steps:', sum(len(g) for g in groups))
jl = [g for g in groups if any(n == 'GetProductHtml' for _, n, _ in g)]
print('groups with GetProductHtml:', len(jl))
for g in jl[:3]:
    print('  0x%x ->' % g[0][0], ', '.join('%d:%s' % (o, n) for _, n, o in g))
io.open('row_groups.json','w',encoding='utf-8').write(json.dumps(
    [{'base': '0x%x' % g[0][0], 'steps': [[o, n] for _, n, o in g]} for g in groups], ensure_ascii=False, indent=1))
print('written row_groups.json')
