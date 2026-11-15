import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for needle in ('Export', 'Pin Group', 'Move Group', 'Link Change', 'Quicktask', 'Quick Task', 'Clock'):
    hits = sorted({r for r in rows if needle.lower() in r.lower() and len(r) < 60})[:6]
    print('== %-14s %d' % (needle, len(hits)))
    for h in hits: print('     ', h)
