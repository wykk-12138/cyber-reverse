import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
hits = [r for r in rows if 'TaskView' in r]
print('TaskView-bearing strings:', len(hits))
seen = set()
for r in hits[:12]:
    key = r[:60]
    if key in seen: continue
    seen.add(key)
    print('   ', r[:150])
