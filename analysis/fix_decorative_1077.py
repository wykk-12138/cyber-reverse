"""R1295 (cont.): the round-1077 mutation became decorative because the assertion I wrote in R1294 was weaker.

The mutation shortened the message to `"... route unrecorded locally");`, which still contains the phrase the new
assertion looks for, so the tests stayed green and the guard proved nothing. The mutation now removes every phrase the
guard depends on — the classification prefix, server-delivered, connect/app and the credential sentence — so a
regression cannot satisfy it by accident.
"""

import io

P = 'D:/projects/cyber-reverse/replica/tools/mutation-check.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

hit = None
for i, l in enumerate(lines):
    if '"replace"' in l and 'farfetch: product route unrecorded locally' in l:
        hit = i
        break

if hit is None:
    raise SystemExit('replace line not found')

lines[hit] = '        "replace": \'            "farfetch: product failed");\','
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('line %d updated ->' % (hit + 1), lines[hit].strip())
print('--only supported:', any('--only' in l for l in lines))
