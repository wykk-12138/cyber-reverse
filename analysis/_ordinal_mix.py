import io, re, collections
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2) for m in (pat.match(l) for l in lines) if m]
owners = collections.defaultdict(set)
for t in rows:
    for m in re.finditer(r'<<(\w+)>b__(\d+)_', t):
        owners[int(m.group(2))].add(m.group(1))
counts = {o: len(v) for o, v in owners.items()}
multi = {o: c for o, c in counts.items() if c >= 2}
print('ordinals carrying lambda owners:', len(counts))
print('ordinals with >=2 DIFFERENT owner names (i.e. provably shared):', len(multi))
avg = sum(counts.values()) / max(1, len(counts))
print('average distinct owner names per ordinal: %.2f' % avg)
worst = sorted(counts.items(), key=lambda kv: -kv[1])[:5]
print('worst ordinals:', worst)
print()
print('所以：同一序号平均挂 %.1f 个不同方法的 lambda —— 单序号推断在构造上就无效。' % avg)
