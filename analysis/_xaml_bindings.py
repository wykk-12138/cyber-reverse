import io, re, json, collections
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]

# Avalonia compiled-XAML descriptors: "<Namespace.Type>,<Owner.Property>!Getter|Setter"
desc = re.compile(r'((?:Cybersole|Avalonia|System)[\w.`]*?),((?:Cybersole|Avalonia|System)[\w.]*?)!(Getter|Setter)')
types = collections.defaultdict(set)
for a, t in rows:
    for m in desc.finditer(t):
        typ, member, kind = m.group(1), m.group(2), m.group(3)
        if not typ.startswith('Cybersole.'):
            continue
        mem = member.split('.')[-1]
        types[typ].add((mem, kind))

print('bound Cybersole types:', len(types))
total = sum(len(v) for v in types.values())
print('bound members:', total)
out = {t: sorted({m for m, _ in v}) for t, v in types.items()}
io.open('xaml_bindings.json', 'w', encoding='utf-8').write(json.dumps(out, indent=1, ensure_ascii=False))
print('written xaml_bindings.json')
for t in sorted(out)[:6]:
    print(' ', t, '->', ', '.join(out[t])[:110])
