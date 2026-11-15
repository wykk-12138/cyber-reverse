import io, json, re
rows = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\row_groups_wide.json', encoding='utf-8'))
cand = [g for g in rows if g['base'].lower().lstrip('0x').startswith('3388f')]
print('candidates:', [g['base'] for g in cand])
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
for g in cand:
    names = {n for _, n in g['steps']}
    print(g['base'], '->', ', '.join('%d:%s' % (o, n) for o, n in g['steps']))
    for f in re.finditer(r'new\("(?P<store>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<body>.*?)\n\s*\}(\s*,\s*FlowSource\.\w+)?\);', src, re.S):
        flow_names = set(re.findall(r'new Step\("([^"]+)"', f.group('body')))
        hit = names & flow_names
        if hit: print('   flow %-22s 命中 %d/%d: %s' % (f.group('store'), len(hit), len(flow_names), ', '.join(sorted(hit))))
