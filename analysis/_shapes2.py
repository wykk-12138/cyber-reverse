import io, re, collections
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]

shape = collections.defaultdict(lambda: collections.defaultdict(set))
for r in rows:
    if '!Property' not in r and '!Getter' not in r and '!Setter' not in r:
        continue
    # split on commas: entries look like "Ns.Type,Cybersole.Member!Kind"
    for chunk in r.replace('&', ',').split(','):
        chunk = chunk.strip()
        if ',Cybersole.' in chunk or not chunk.startswith('Cybersole.'):
            continue
    for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
        member = m.group(1); kind = m.group(2)
        # the type is the token right before ",Cybersole.member"
        idx = r.find(',Cybersole.' + member + '!' + kind)
        if idx <= 0: continue
        head = r[:idx]
        t = re.split(r'[,\s]', head)[-1].split('.')[-1]
        shape[t][member].add(kind)

for t in ('CreateModel', 'BotTask', 'TaskGroup', 'Solver', 'GoogleAccountsView'):
    if t in shape:
        print('==', t)
        for member, kinds in sorted(shape[t].items()):
            print('    %-26s %s' % (member, ','.join(sorted(kinds))))
print('types with accessor evidence:', len(shape))
