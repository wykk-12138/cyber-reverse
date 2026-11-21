"""Decode cartApiObjectCreate and check which Shopify endpoint shape it wants."""

import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SOURCE = 0x1470EF5FC
OUT = 'analysis/.shopify_storefront_docs.json'


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


def read_string(chars_va):
    length = int.from_bytes(bytes_at(chars_va - 12, 12)[8:12], 'little')
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


document = read_string(SOURCE)
declared = sorted(set(re.findall(r'\$(\w+)\s*:', document)))
print('cartApiObjectCreate: %d chars' % len(document))
print('  head: %s' % document[:110].replace('\n', ' ').replace('\r', ''))
print('  declares: %s' % declared)

io.open(OUT, 'w', encoding='utf-8', newline='').write(
    json.dumps({'cart_api_object_create': document}, ensure_ascii=False, indent=1, sort_keys=True))
print('wrote %s' % OUT)
