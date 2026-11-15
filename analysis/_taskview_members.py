import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
blob = '\n'.join(r for r in rows if 'Cybersole.Ui.Views.Tasks.TaskView' in r)
members = sorted(set(re.findall(r'Cybersole\.Ui\.Views\.Tasks\.TaskView,Cybersole\.(\w+)!(\w+)', blob)))
print('TaskView bound members with accessor evidence:', len(members))
for m, k in members:
    print('    %-22s %s' % (m, k))
