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
        # R1112: a markup extension or converter sits in the first position as the BINDING HELPER,
        # never as the owner, so the second group's property belongs to the owner and not to it.
        # Measured over 2,474 descriptor pairs: the four Localize*Extension types appear only here
        # (15 occurrences) and never in the owner position (the sole non-app owner-position hit is
        # the framework's Avalonia.Base.Converter). Record the type with NO members rather than
        # dropping it -- dropping it would hide a real absence from the replica.
        if typ.split('.')[-1].split('`')[0].endswith(('Extension', 'Converter')):
            types[typ]
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
