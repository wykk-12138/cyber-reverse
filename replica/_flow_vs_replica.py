import io, re, json
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\CandidateSteps.cs', encoding='utf-8').read()
# pull each flow block: Name = "...", Steps = { Step("X", n), ... }
flows = re.findall(r'Flow\(\s*"(?P<store>[^"]+)"[^)]*?new\[\]\s*\{(?P<body>.*?)\}\s*\)', src, re.S)
print('flows parsed:', len(flows))
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\row_groups_wide.json', encoding='utf-8'))
A = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))
pool = []
for g in segs:
    pool.append(('B', g['base'], [(o, n) for o, n in g['steps']]))
for s in A:
    pool.append(('A', s['addr'], [(o, n) for o, n in s['steps']]))

for m in flows:
    store = m.group('store')
    names = [n for n in re.findall(r'Step\("([^"]+)"', m.group('body'))]
    if not names: continue
    best = None
    for kind, base, steps in pool:
        seg = {n for _, n in steps}
        hit = len(set(names) & seg)
        if best is None or hit > best[0]:
            best = (hit, kind, base, len(seg))
    print('%-14s %2d 步  最佳匹配: %s %s 命中 %d / %d' % (store, len(names), best[1], best[2], best[0], best[3]))
    if best[0] < len(names) * 0.5:
        print('     未命名步:', ', '.join([n for n in names if n not in {x for _, x in [s for k, b, s in pool if b == best[2]][0]}] [:6]))
