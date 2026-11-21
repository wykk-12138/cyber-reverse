"""setShippingAddress is 4992 characters and sits beside the billing mutation's range.

Billing (4989) went to Highsnobiety because it declares an action object plus two locales. Shipping is 4992 — almost
the same length — and sits at 0x1470fa944, in a block of its own. If it declares the same shape, the store gets its
third step; if not, it belongs somewhere else and the length is a coincidence.

Usage: python analysis/check_shipping_address.py
"""
import io
import json
import re
import subprocess
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

TARGETS = {
    'setShippingAddress': 0x1470FA944,
    'updateShipAddress': 0x1470FD394,
    'updateMyPaymentWithActions': 0x1470FD05C,
}


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


for name, address in TARGETS.items():
    text = read_string(address)
    declared = sorted(set(re.findall(r'\$(\w+)\s*:', text)))
    print('%-28s %5d chars  %s' % (name, len(text), text[:70].replace('\n', ' ').replace('\r', '')))
    print('%-28s declares %s' % ('', declared))

    sites = subprocess.run([sys.executable, 'analysis/disp32_scan_any.py', hex(address - 12)],
                           capture_output=True, text=True).stdout
    first = re.search(r'VA (0x[0-9A-Fa-f]+)\n', sites)
    print('%-28s first site: %s' % ('', first.group(1) if first else 'none'))
    if first:
        info = subprocess.run([sys.executable, 'analysis/site_to_func.py', first.group(1)],
                              capture_output=True, text=True).stdout
        match = re.search(r'func (0x[0-9A-Fa-f]+)\.\.(0x[0-9A-Fa-f]+)', info)
        print('%-28s function: %s' % ('', match.group(0) if match else 'none'))
    print()
