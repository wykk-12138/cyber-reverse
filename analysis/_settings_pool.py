import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = []
for ln in lines:
    m = pat.match(ln)
    if m: rows.append((m.group(1), m.group(2)))
for want in ['Version ', '5.18.32', 'Quicks', 'Time remaining', 'Queue Presentation', 'CHECK FOR UPDATES', 'Currency']:
    hits = [(a, t) for a, t in rows if want in t and len(t) < 120]
    print('==', repr(want), len(hits))
    for a, t in hits[:5]:
        print('   ', a, repr(t))
