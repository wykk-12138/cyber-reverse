import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
for needle in ('TaskGroup.Pinned', 'TaskGroup.Order', 'Pinned', 'GroupOrder'):
    hits = [r for r in rows if needle in r and 'TaskGroup' in r]
    print('%-18s %d' % (needle, len(hits)), hits[:3])
print()
for k in ('TaskGroup.Manual', 'TaskGroup.ResetLimitsAfter', 'TaskGroup.ResettingAt', 'TaskGroup.ResetButton', 'TaskGroup.PeriodStart.Tooltip', 'TaskGroup.Tab.Delays.Tooltip'):
    v = [r for r in rows if r.startswith('"' + k + '"')][:2]
    print('%-34s %s' % (k, v[0][:100] if v else '—'))
