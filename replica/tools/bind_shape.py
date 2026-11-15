import io, re, collections, json, sys

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
BINDS = r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json'

def accessors():
    lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
    rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
    shape = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
            member, kind = m.group(1), m.group(2)
            idx = r.find(',Cybersole.' + member + '!' + kind)
            if idx <= 0:
                continue
            head = r[:idx]
            t = re.split(r'[,\s]', head)[-1].split('.')[-1]
            shape[t][member].add(kind)
    return shape

def main():
    shape = accessors()
    binds = json.load(io.open(BINDS, encoding='utf-8'))
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for full, members in sorted(binds.items()):
        short = full.split('.')[-1]
        if only and only.lower() not in short.lower():
            continue
        ev = shape.get(short)
        if not ev:
            continue
        print('==', short)
        for m in sorted(members):
            kinds = ev.get(m)
            print('    %-26s %s' % (m, ','.join(sorted(kinds)) if kinds else '- (no accessor evidence)'))
    print('types with accessor evidence:', len(shape))

main()
