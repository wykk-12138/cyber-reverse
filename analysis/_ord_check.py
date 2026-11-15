import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
flows = {}
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    flows[m.group('s')] = [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))]

lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = {m.group(1): m.group(2) for m in (pat.match(l) for l in lines) if m}

addrs = {
 'structure-token-multi': ['0x034b14b8'], 'structure-token-single': ['0x034b23a5'],
 'popmart': ['0x0337b9e5'], 'demandware-classic': ['0x034ac0f3'],
 'demandware-dual': ['0x0336f0bd'], 'collectplus-app': ['0x033929ec'],
 'nike': ['0x03385576', '0x0338562c'], 'johnlewis': ['0x0338a655'],
}
print('flow                  literal 步数  flow 步数   序号可解释(去掉粘连位)')
for store, alist in addrs.items():
    lit = []
    for a in alist:
        lit += [(n, int(o)) for n, o in re.findall(r'<(\w+)>d__(\d+)', rows[a])]
    flow = flows[store]
    # for johnlewis the two lambda steps are inserted at 21/22
    extra = [s for s in flow if s[0] not in {n for n, _ in lit}]
    explain, bad = 0, []
    litmap = dict(lit)
    for name, o in flow:
        if name in litmap:
            lo = litmap[name]
            if lo == o or str(lo).startswith(str(o)) or str(lo).rstrip('0') == str(o) or (lo // 10) == o:
                explain += 1
            else:
                bad.append((name, lo, o))
    print('%-22s %2d       %2d       %2d/%2d   %s' % (store, len(lit), len(flow), explain, len(flow), bad[:3] or ('插补: ' + str([e[0] for e in extra]) if extra else '')))
