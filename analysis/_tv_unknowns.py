import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
keys = sorted({r.split('"')[1] for r in rows if r.startswith('"') and ('Quicktask' in r or 'MoveGroup' in r or 'Toggle' in r or 'LinkChange' in r) and '":' in r})
print('locale keys:', len(keys))
for k in keys: print('   ', k)
print()
for needle in ('Quicktask', 'MoveGroup', 'Toggle', 'LinkChange'):
    hits = [r for r in rows if needle in r and 'Cybersole' in r][:4]
    print('== %-11s %d' % (needle, len(hits)))
    for h in hits: print('    ', h[:120])
