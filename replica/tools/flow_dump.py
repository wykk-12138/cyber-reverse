import io, json, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
d_state = re.compile(r'<(\w+)>d__(\d+)')
lam = re.compile(r'<(\w+)>b__(\d+)_')

seqs = []
for idx, (a, t) in enumerate(rows):
    ds = d_state.findall(t)
    ls = lam.findall(t)
    if len(ds) >= 2 and ls:
        seqs.append({
            'addr': a,
            'steps': [[int(o), n] for n, o in ds],
            'lambdas': sorted({int(o) for _, o in ls}),
            'neighbours': [rows[j][1][:40] for j in range(max(0, idx-2), min(len(rows), idx+3))],
        })
seqs.sort(key=lambda s: s['steps'][0][0])
io.open('flow_step_sequences.json', 'w', encoding='utf-8').write(json.dumps(seqs, ensure_ascii=False, indent=1))
print('literals with a step sequence:', len(seqs))
print('total steps recovered:', sum(len(s['steps']) for s in seqs))
print()
for s in seqs[:5]:
    print(s['addr'], '->', ', '.join('%d:%s' % (o, n) for o, n in s['steps'][:8]), '...')
    print('   邻居:', ' | '.join(s['neighbours'][:3]))
