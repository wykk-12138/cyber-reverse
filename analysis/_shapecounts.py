import io, re, collections
POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
shape = collections.defaultdict(lambda: collections.defaultdict(set))
for r in rows:
    for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
        member, kind = m.group(1), m.group(2)
        idx = r.find(',Cybersole.' + member + '!' + kind)
        if idx <= 0: continue
        t = re.split(r'[,\s]', r[:idx])[-1].split('.')[-1]
        shape[t][member].add(kind)
total = sum(len(v) for v in shape.values())
with_set = sum(1 for v in shape.values() for k in v.values() if 'Setter' in k)
get_only = sum(1 for v in shape.values() for k in v.values() if 'Setter' not in k)
print('members with accessor evidence:', total)
print('  settable:', with_set, ' getter-only:', get_only)
