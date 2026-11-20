"""List CasioFlow's overrides and session keys, to a file.

Written because piping this through the console keeps dying on a euro sign in a nearby string: this
terminal renders UTF-8 as GBK. A file has no opinion about encoding.
"""
import io

SRC = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
OUT = 'analysis/.casio_flow_map.txt'

lines = io.open(SRC, encoding='utf-8').read().splitlines()
start = None
for index, line in enumerate(lines, 1):
    if 'class CasioFlow' in line:
        start = index
if start is None:
    raise SystemExit('CasioFlow not found')

out = []
for index in range(start, len(lines) + 1):
    line = lines[index - 1]
    stripped = line.strip()
    if index > start and 'class ' in line and 'CasioFlow' not in line:
        out.append('%d  [next class] %s' % (index, stripped[:90]))
        break
    if ('override' in line or 'const ' in line or 'Vars[' in line or 'public ' in line):
        out.append('%d  %s' % (index, stripped[:130]))

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print('wrote %s (%d lines)' % (OUT, len(out)))
