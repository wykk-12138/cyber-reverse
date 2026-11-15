import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
flows = {}
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    flows[m.group('s')] = [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))]

lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = {m.group(1): m.group(2) for m in (pat.match(l) for l in lines) if m}

for store, addrs in (('nike', ['0x03385576', '0x0338562c']), ('johnlewis', ['0x0338a655'])):
    literal = []
    for a in addrs:
        literal += [(n, int(o)) for n, o in re.findall(r'<(\w+)>d__(\d+)', rows[a])]
    flow = flows[store]
    print('== %-10s literal %d 步（%s）/ flow %d 步' % (store, len(literal), '+'.join(addrs), len(flow)))
    print('   literal:', ', '.join('%s(%d)' % (n, o) for n, o in literal))
    print('   flow   :', ', '.join('%s(%d)' % (n, o) for n, o in flow))
    print('   同序:', [n for n, _ in literal] == [n for n, _ in flow])
