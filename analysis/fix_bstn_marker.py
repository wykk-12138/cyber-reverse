"""Put the R294 marker on the line that actually names /api/beast (R1284).

The ratchet binds per path and per line: any non-comment line containing the path must carry the marker itself.
"""

import io

P = 'src/Cybersole.Stores/Flows/BstnFlow.cs'
text = io.open(P, encoding='utf-8').read()

old = ('            "bstn: cart route unrecorded — /cart.js answers 404 and /api/beast is live-proven only for " +\n'
       '        "geoIP and monetate, so the add route is not attested " +  // inferred: no image evidence (R294)\n'
       '            "at a path not yet captured"));')

new = ('            // inferred: no image evidence — ida.py str answers 0 for bstn, BSTN, bstn.com and beast/geoIP\n'
       '            "bstn: cart route unrecorded — /api/beast answers for geoIP and monetate, " +\n'
       '            "its cart child route is not attested; /cart.js answers 404 at the store"));')

if old not in text:
    raise SystemExit('anchor missing')
text = text.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('rewritten; marker lines:', sum('inferred: no image evidence' in l for l in text.split('\n')))
