"""Read the inline URL bytes the Product sender builds.

The sender writes eleven characters into a buffer from a 16-byte constant plus a dword plus a word, then appends
"api/graphql" — so the host is in that constant and not in a normal string object. Read it both ways and see which
one produces a host.
"""

import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            reply = json.loads(reply.splitlines()[0])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


raw = bytes_at(0x145E99C50, 16)
print('constant bytes: %s' % raw.hex())
print('  as ascii:  %r' % raw.decode('ascii', errors='replace'))
print('  as utf-16: %r' % raw.decode('utf-16-le', errors='replace'))

tail = bytes_at(0x145E99C50, 32)
print('wider read:')
print('  as ascii:  %r' % tail.decode('ascii', errors='replace'))
print('  as utf-16: %r' % tail.decode('utf-16-le', errors='replace'))
