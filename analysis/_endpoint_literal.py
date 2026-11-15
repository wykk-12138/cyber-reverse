import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
flows = []
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    steps = re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))
    if 'Literal' not in (m.group('tail') or ''):
        flows.append((m.group('s'), steps))

lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
state = [(a, dict((n, int(o)) for n, o in re.findall(r'<(\w+)>d__(\d+)', t)), t) for a, t in rows]
state = [s for s in state if len(s[1]) >= 2]

for store, steps in flows:
    names = [n for n, _ in steps]
    best = max(state, key=lambda s: len(set(s[1]) & set(names)))
    hit = set(best[1]) & set(names)
    print('== %-20s %2d 步  最佳单行命中 %2d  (at %s)' % (store, len(names), len(hit), best[0]))
    missing = [n for n in names if n not in best[1]]
    print('   该行含而流程缺:', ', '.join(sorted(set(best[1]) - set(names))[:6]) or '-')
    print('   流程有而该行无:', ', '.join(missing[:6]) or '-')
