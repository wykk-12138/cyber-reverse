import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
wh = [r for r in rows if r.startswith('Settings.Webhook')]
for h in wh: print('   ', h[:100])
print()
print('含 Extra. 的键:', len([r for r in rows if '.Extra.' in r]))
for r in [x for x in rows if '.Extra.' in x][:10]: print('   ', r[:100])
