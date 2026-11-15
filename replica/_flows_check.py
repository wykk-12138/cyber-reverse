import io, re, json
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
# each flow: new("store", new[] { new Step("Name", ord), ... })
flows = []
for m in re.finditer(r'new\("(?P<store>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<body>.*?)\n\s*\}\);', src, re.S):
    names = re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('body'))
    if names: flows.append((m.group('store'), names))
print('flows in StoreFlowSteps:', len(flows))

pool = []
for g in json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\row_groups_wide.json', encoding='utf-8')):
    pool.append(('B', g['base'], {n for _, n in g['steps']}))
for s in json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8')):
    pool.append(('A', s['addr'], {n for _, n in s['steps']}))

print()
print('%-12s %3s  %-6s %-12s %s' % ('flow', '步', '命中', '最佳段', '未命中的步'))
for store, steps in flows:
    names = {n for n, _ in steps}
    best = max(pool, key=lambda p: len(names & p[2]))
    hit = len(names & best[2])
    missing = [n for n, _ in steps if n not in best[2]]
    print('%-12s %3d  %2d/%-3d %-12s %s' % (store, len(names), hit, len(names), best[1], ', '.join(missing[:5]) or '—'))
