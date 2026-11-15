import io, re, collections
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]

d_state = re.compile(r'<([A-Za-z0-9_]+)>d__(\d+)')      # state machines: <Method>d__N
lam = re.compile(r'<([A-Za-z0-9_]+)>b__(\d+)_(\d+)')     # lambda tables: <Method>b__N_M

by_ord_state = collections.defaultdict(set)
by_ord_lam = collections.defaultdict(set)
for a, t in rows:
    for name, o in d_state.findall(t):
        by_ord_state[int(o)].add(name)
    for name, o, _ in lam.findall(t):
        by_ord_lam[int(o)].add(name)

print('ordinals seen in d__ runs      :', len(by_ord_state))
print('ordinals seen in lambda tables :', len(by_ord_lam))

print('\n== 两个来源同时出现在同一序号上的名字（互相印证）==')
agree = 0
for o in sorted(set(by_ord_state) & set(by_ord_lam)):
    both = by_ord_state[o] & by_ord_lam[o]
    if both:
        agree += 1
        print('  %4d  %s' % (o, ', '.join(sorted(both))[:100]))
print('合计', agree, '个序号有两源同名')

print('\n== 缺口区间 118..135 的两源情况 ==')
for o in range(118, 136):
    s = ', '.join(sorted(by_ord_state.get(o, set())))[:60]
    l = ', '.join(sorted(by_ord_lam.get(o, set())))[:60]
    flag = 'AGREE' if (by_ord_state.get(o, set()) & by_ord_lam.get(o, set())) else ''
    print('  %4d  d__: %-42s lam: %-42s %s' % (o, s or '-', l or '-', flag))
