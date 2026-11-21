"""Find the documents the two senders carry.

The senders reference their document through the *object* header — twelve bytes before the characters — so
`names_at` reports those offsets as `raw`, not `str`, and a filter on `str` misses exactly the thing we want.
This walks every literal offset in the function and tries to read a string at offset+12.

Usage: python analysis/highsnobiety_docs2.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

TARGETS = {
    'fetchProduct': 0x140B57020,
    'setCustomerEmail': 0x140B58920,
}

TEMP = os.environ.get('TEMP', '.')


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True).stdout


def bytes_at(address, size):
    import json as _json
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        reply = _json.loads(reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


def try_string(object_address):
    try:
        header = bytes_at(object_address - 12, 12)
        length = int.from_bytes(header[8:12], 'little')
        if not 200 < length < 40000:
            return None
        first = bytes_at(object_address, 120).decode('utf-16-le', errors='replace')
        return first, length
    except Exception:
        return None


for name, address in TARGETS.items():
    path = os.path.join(TEMP, 'r1339d_%x.c' % address)
    run(['analysis/dump_dec.py', hex(address), path])
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(int(offset, 16) for offset in re.findall(r'&?off_([0-9A-F]{9})', text)))
    print('=== %s %#x' % (name, address))
    for offset in offsets:
        for candidate in (offset, offset + 12, offset - 12):
            found = try_string(candidate)
            if found and ('mutation' in found[0] or 'query' in found[0] or 'fragment' in found[0]):
                print('   document at %#x (via %#x), %d chars' % (candidate, offset, found[1]))
                print('   %s' % found[0][:100].replace('\n', ' ').replace('\r', ''))
                break
    print()
