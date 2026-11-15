import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for w in ('Bearer','License','Timeout','Startup','Clock','EnableClock','ClockFormat'):
    hits = [r for r in rows if w.lower() in r.lower() and len(r) < 60]
    print('== %-12s %d' % (w, len(hits)))
    for h in hits[:4]: print('     ', h)
