import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
flows = []
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    steps = re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))
    tail = m.group('tail') or ''
    source = 'Literal' if 'Literal' in tail else 'Endpoint'
    flows.append((m.group('s'), source, steps))

pool = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read()
d_names = set(re.findall(r'<(\w+)>d__\d+', pool))
print('names with a d__ state machine in the pool:', len(d_names))
print()
for store, source, steps in flows:
    names = [n for n, _ in steps]
    hit = [n for n in names if n in d_names]
    print('%-22s %-9s %2d 步  池中 d__ 命中 %2d' % (store, source, len(names), len(hit)))
    if 0 < len(hit) < len(names):
        miss = [n for n in names if n not in d_names]
        print('     无 d__:', ', '.join(miss[:7]))
