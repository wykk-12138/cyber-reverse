import io, re, json, collections
POOL = 'analysis/pe_strings.txt'
BINDS = r'replica/docs/xaml_bindings.json'
lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
shape = collections.defaultdict(set)
for r in rows:
    for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
        member, kind = m.group(1), m.group(2)
        idx = r.find(',Cybersole.' + member + '!' + kind)
        if idx <= 0: continue
        t = re.split(r'[,\s]', r[:idx])[-1].split('.')[-1]
        shape[t].add(member)
binds = {k.split('.')[-1]: set(v) for k, v in json.load(io.open(BINDS, encoding='utf-8')).items()}
missing_types = sorted(set(shape) - set(binds))
extra_members = {t: sorted(shape[t] - binds.get(t, set())) for t in shape if shape[t] - binds.get(t, set())}
print('types in accessor evidence:', len(shape))
print('types present in xaml_bindings.json:', len(binds))
print('types ONLY in accessor evidence:', len(missing_types))
for t in missing_types[:12]: print('   +', t, '(%d members)' % len(shape[t]))
print()
print('types whose member list is INCOMPLETE in the json:', len(extra_members))
for t, ms in list(extra_members.items())[:10]:
    print('   %-26s +%d  %s' % (t, len(ms), ', '.join(ms[:8])))
print()
print('total members named only by the accessor evidence:',
      sum(len(v) for v in extra_members.values()) + sum(len(shape[t]) for t in missing_types))
