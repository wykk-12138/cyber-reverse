import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for pref in ('SmartActions.Template', 'SmartActions.Use', 'Template.'):
    hits = sorted({r for r in rows if r.startswith(pref)})
    print('== %-24s %d' % (pref, len(hits)))
    for h in hits[:10]: print('    ', h)
print()
print('含 Template 的键/文案（限 60 字符）:')
for r in sorted({r for r in rows if 'Template' in r and len(r) < 60})[:16]: print('   ', r)
