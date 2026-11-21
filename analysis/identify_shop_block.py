"""Are ShopProductSearch, addToCart and buynow the Shop app family, or a store's?

ProductDetails came from server.shop.app. If these belong to the same API, one class finishes the surface; if not,
they are something else and must not be folded in on the strength of their address alone.
"""

import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

TARGETS = {
    'shop_product_search': 0x140D26050,
    'add_to_cart_or_buynow': 0x140B60250,
}
TEMP = os.environ.get('TEMP', '.')


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
    if not 0 < length < 40000:
        return None
    chunks = []
    offset = 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


for label, address in TARGETS.items():
    path = os.path.join(TEMP, 'r1347_%s.c' % label)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(address), path],
                   capture_output=True, text=True)
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout
    strings = [line.split("'", 2)[1] for line in out.splitlines() if ' str ' in line and "'" in line]
    hosts = [s for s in strings if s.startswith('http') or 'shop' in s.lower() or 'app' in s.lower()]
    print('=== %s  %#x' % (label, address))
    print('    hosts/labels: %s' % hosts[:6])
    print('    literals: %s' % ' | '.join(strings[:12]))
    print()
