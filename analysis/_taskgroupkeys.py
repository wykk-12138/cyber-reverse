import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
keys = sorted({r.split('"')[1] for r in rows if r.startswith('"TaskGroup.') or r.startswith('"GroupModal.')})
print('TaskGroup./GroupModal. keys:', len(keys))
for k in keys: print('   ', k)
