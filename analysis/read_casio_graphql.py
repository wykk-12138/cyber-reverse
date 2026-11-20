"""Read the Casio product-search GraphQL document out of the image, as UTF-16, to a file.

The console renders UTF-8 as GBK and dies on the first character it cannot map, which is why every attempt
to print this string inline ended in a traceback rather than the string. A file has no such opinion.
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

BASE = 0x146A75000
SPAN = 0x1000
OUT = 'analysis/.casio_graphql.txt'

res = call('get_bytes', {'regions': [{'addr': hex(BASE), 'size': SPAN}]})
if isinstance(res, str):
    res = json.loads(res)
blob = bytes(int(t, 16) for t in res[0]['data'].split())

# The document is UTF-16LE. Take the printable runs so the query can be read out of the surrounding
# metadata without guessing where it starts.
text = blob.decode('utf-16-le', errors='replace')
runs = []
current = []
for ch in text:
    if ch.isprintable():
        current.append(ch)
    else:
        if len(current) > 12:
            runs.append(''.join(current))
        current = []
if len(current) > 12:
    runs.append(''.join(current))

io.open(OUT, 'w', encoding='utf-8').write('\n\n'.join(runs))
print('wrote %s with %d run(s)' % (OUT, len(runs)))
for index, run in enumerate(runs):
    print('run %d: %d chars' % (index, len(run)))
