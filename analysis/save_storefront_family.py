"""The other four operations of the api/graphql family: documents and their variables."""

import io
import json
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

SITES = {
    'add_item_to_cart': 0x1470CB3F4,
    'create_initial_cart': 0x1470CF25C,
    'checkout_cart': 0x14711CF9C,
    'get_session': 0x147146994,
}
OUT = 'analysis/.storefront_api_docs.json'


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


documents = json.loads(io.open(OUT, encoding='utf-8').read())
for name, address in SITES.items():
    text = read_string(address)
    documents[name] = text
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', text)))
    print('%-20s %5d chars  declares %s' % (name, len(text), declared))
    print('                     head: %s' % text[:70].replace('\n', ' ').replace('\r', ''))

io.open(OUT, 'w', encoding='utf-8', newline='').write(
    json.dumps(documents, ensure_ascii=False, indent=1, sort_keys=True))
print('wrote %s' % OUT)
