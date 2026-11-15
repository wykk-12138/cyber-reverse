import io, re, collections
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]

pat = re.compile(r'([\w.]+?),\s*Cybersole\.(\w+)!(Property|Getter|Setter)')
shape = collections.defaultdict(lambda: collections.defaultdict(set))
for r in rows:
    for m in pat.finditer(r):
        t = m.group(1).split('.')[-1]
        shape[t][m.group(2)].add(m.group(3))

for t in ('CreateModel', 'BotTask', 'TaskGroup', 'Solver'):
    if t in shape:
        print('==', t)
        for member, kinds in sorted(shape[t].items()):
            print('    %-24s %s' % (member, ','.join(sorted(kinds))))
print('types with accessor evidence:', len(shape))
