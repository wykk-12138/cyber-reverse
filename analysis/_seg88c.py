import io, json, re
d = json.load(io.open('docs/flow_step_sequences.json', encoding='utf-8'))
g = [x for x in d if x['addr'] == '0x03388fd2'][0]
print('A-layout segment 0x03388fd2:', ', '.join('%d:%s' % (o, n) for o, n in g['steps']))
src = io.open('src/Cybersole.Stores/Flows/StoreFlowSteps.cs', encoding='utf-8').read()
names = {n for _, n in g['steps']}
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n\s*\}(\s*,\s*FlowSource\.\w+)?\);', src, re.S):
    fn = set(re.findall(r'new Step\("([^"]+)"', m.group('b')))
    hit = names & fn
    if hit:
        print('  flow %-24s 命中 %d/%d -> %s' % (m.group('s'), len(hit), len(fn), ', '.join(sorted(hit))))
