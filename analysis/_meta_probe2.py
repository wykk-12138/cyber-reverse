import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
print('pool rows', len(rows))
probes = {
 'namespace-qualified method sigs': r'Cybersole\.[A-Za-z0-9_.]+\.[A-Za-z0-9_]+[,)]',
 'System.Void Cybersole': r'System\.Void Cybersole',
 'Type name + method list blob': r'<\w+>k__BackingField',
 'Full member signature': r'\b(Cybersole\.[A-Za-z0-9_.]+)::([A-Za-z0-9_]+)',
}
for label, rx in probes.items():
    hits = [(a, t) for a, t in rows if re.search(rx, t)]
    print('==', label, len(hits))
    for a, t in hits[:4]:
        print('   ', a, t[:130])
