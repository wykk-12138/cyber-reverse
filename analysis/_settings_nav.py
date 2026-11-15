import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
nav = sorted({r for r in rows if r.startswith('Settings.Nav.')})
print('Settings.Nav.* keys:', len(nav))
for k in nav: print('   ', k)
print()
aycd = sorted({r for r in rows if r.startswith('Settings.Aycd.')})
print('Settings.Aycd.* keys:', len(aycd))
for k in aycd[:8]: print('   ', k)
