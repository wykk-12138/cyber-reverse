"""R1338: decode the Highsnobiety documents (fixed reply shape).

`get_bytes` answers as a list on some sizes and as a JSON string on others — the same trap that bit the 8 KiB
chunking in an earlier round. This normalises the reply before reading it, and prints the length the object
header claims beside the length actually read, so a mismatch is visible rather than silent.

Usage: python analysis/save_highsnobiety_docs.py
"""
import io
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

OUT = 'analysis/.highsnobiety_docs.json'
SITES = {
    'add_line_item': 0x1470E6CDC,
    'add_discount_code': 0x1470E5234,
}


def bytes_at(address, size):
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        reply = json.loads(reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def read_string(chars_va):
    header = bytes_at(chars_va - 12, 12)
    length = int.from_bytes(header[8:12], 'little')
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want

    text = b''.join(chunks).decode('utf-16-le', errors='replace')
    print('   header says %d chars, read %d' % (length, len(text)))
    return text[:length]


documents = {}
for name, address in SITES.items():
    print('%-20s %#x' % (name, address))
    text = read_string(address)
    documents[name] = text
    print('   %s' % text[:80].replace('\n', ' '))

with io.open(OUT, 'w', encoding='utf-8', newline='') as handle:
    json.dump(documents, handle, ensure_ascii=False, indent=1, sort_keys=True)
print('wrote %s' % OUT)
