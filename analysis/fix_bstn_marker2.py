"""Put the marker on the same physical line as /api/beast (R1284)."""

import io

P = 'src/Cybersole.Stores/Flows/BstnFlow.cs'
text = io.open(P, encoding='utf-8').read()

old = '            "bstn: cart route unrecorded — /api/beast answers for geoIP and monetate, " +\n'
new = ('            "bstn: cart route unrecorded — /api/beast answers for geoIP and monetate, " +\n'
       '            // inferred: no image evidence — the marker sits on the string line above by necessity: the\n'
       '            // ratchet binds a path to the line that names it, and that line is this literal\n')

if old not in text:
    raise SystemExit('anchor missing')
text = text.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)

for i, line in enumerate(text.split('\n'), 1):
    if '/api/beast' in line and not line.lstrip().startswith('//'):
        print('line %d: %s' % (i, line.strip()[:100]))
        print('  has marker:', 'inferred: no image evidence' in line)
