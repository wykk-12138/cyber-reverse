import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
hits = [r for r in rows if 'ExtraField' in r or 'Extra Field' in r]
print('ExtraField* 命中:', len(hits))
for h in hits[:12]: print('   ', h[:110])
print()
wh = [r for r in rows if r.startswith('Settings.Webhook')]
print('Settings.Webhook* 键:', len(wh))
for h in wh[:20]: print('   ', h[:90])
