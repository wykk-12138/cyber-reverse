import io, json, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
A = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))
segs = {s['addr']: [(o, n) for o, n in s['steps']] for s in A}

def flow(name):
    m = re.search(r'new\("%s", new\[\]\s*\{(.*?)\n    \}, FlowSource\.Literal\);' % re.escape(name), src, re.S)
    return [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group(1))]

for name, addr in (('structure-token-multi', '0x034b14b8'), ('structure-token-single', '0x034b23a5')):
    f = flow(name)
    seg = segs[addr]
    fset, sset = set(n for n, _ in f), set(n for _, n in seg)
    print('==', name, '->', addr)
    print('   flow:', ', '.join('%s(%d)' % (n, o) for n, o in f))
    print('   seg :', ', '.join('%s(%d)' % (n, o) for o, n in seg))
    print('   only in flow:', sorted(fset - sset) or '-')
    print('   only in seg :', sorted(sset - fset) or '-')
