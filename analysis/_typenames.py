import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
tname = re.compile(r'\bCybersole\.[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+\b')
names = {}
for a, t in rows:
    for m in tname.findall(t):
        pass
    for m in re.finditer(r'Cybersole\.[A-Za-z0-9_.]+', t):
        s = m.group(0)
        if s not in names:
            names[s] = a
print('distinct Cybersole.* names:', len(names))
# how many look like types (no lowercase-only last segment? just show samples)
sample = sorted(names.items(), key=lambda kv: kv[1])[:12]
for s, a in sample:
    print('  ', a, s[:80])
print('--- 含 Flow / Store 的 ---')
shown = 0
for s, a in sorted(names.items(), key=lambda kv: kv[1]):
    if 'Flow' in s or 'Store' in s:
        print('  ', a, s[:90]); shown += 1
        if shown >= 12: break
