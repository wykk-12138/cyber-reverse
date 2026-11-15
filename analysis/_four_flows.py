import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
flows = {}
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    flows[m.group('s')] = [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))]

lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]

targets = {'popmart': '0x0337b9e5', 'demandware-classic': '0x034ac0f3',
           'demandware-dual': '0x0336f0bd', 'collectplus-app': '0x033929ec'}
for store, addr in targets.items():
    row = [t for a, t in rows if a == addr][0]
    literal = [(n, int(o)) for n, o in re.findall(r'<(\w+)>d__(\d+)', row)]
    flow = flows[store]
    same_order = [n for n, _ in literal] == [n for n, _ in flow]
    same_ord = [o for _, o in literal] == [o for _, o in flow]
    print('== %-20s literal %2d 步 / flow %2d 步   名字顺序一致:%s   序号一致:%s'
          % (store, len(literal), len(flow), same_order, same_ord))
    if not same_order:
        for i, (a, b) in enumerate(zip([n for n, _ in literal], [n for n, _ in flow])):
            if a != b:
                print('   第一个不同: 位 %d literal=%s(%d) flow=%s(%d)'
                      % (i, a, literal[i][1], b, flow[i][1])); break
    elif not same_ord:
        print('   literal 序号:', ', '.join(str(o) for _, o in literal))
        print('   flow    序号:', ', '.join(str(o) for _, o in flow))
