"""R1295 (cont.): the farfetch find anchor also lost its closing `");` in my first attempt."""

import io

P = 'D:/projects/cyber-reverse/replica/tools/mutation-check.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

hit = None
for i, l in enumerate(lines):
    if 'farfetch: product endpoint unknown' in l and '"find"' in l:
        hit = i
        break

if hit is None:
    raise SystemExit('anchor line not found')

lines[hit] = ('        "find": \'            "farfetch: product route unrecorded locally \u2014 it is a '
              'server-delivered connect/app config entry, schema needs the original login to capture");\',')

io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('line %d updated' % (hit + 1))
print(lines[hit][:150])
