"""R1372: what does AddressInput look like? Read the candidate field strings and see who uses them.

The type name itself does not appear as a string, so the shape has to come from the field names that a sender writes
into an address object. Four candidates showed up exactly once each (addressLine1, addressLine2, recipientName,
locality) and one of them sits close to the other two, which is worth reading.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

CANDIDATES = {
    'addressLine1': 0x146F6EC6C,
    'addressLine2': 0x146F6EC9C,
    'recipientName': 0x147149A94,
    'locality': 0x146FC9852,
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
    chunks, offset = [], 0
    while offset < length * 2:
        want = min(8192, length * 2 - offset)
        chunks.append(bytes_at(chars_va + offset, want))
        offset += want
    return b''.join(chunks).decode('utf-16-le', errors='replace')[:length]


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for name, address in CANDIDATES.items():
    try:
        text = read_string(address)
    except Exception as error:  # noqa: BLE001 - a bad address is information, not a crash
        print('%-14s %#x  unreadable (%s)' % (name, address, type(error).__name__))
        continue
    print('%-14s %#x  %r' % (name, address, text[:90]))

print()
# Where do they live, and who references them?
for name, address in CANDIDATES.items():
    for form, tag in ((address - 12, 'header'), (address, 'chars')):
        sites = run('analysis/disp32_scan_any.py', hex(form))
        found = re.findall(r'VA (0x[0-9A-Fa-f]{9})', sites)
        if not found:
            continue
        print('%-14s %s -> %d site(s): %s' % (name, tag, len(found), ' '.join(found[:3])))
        mapped = run('analysis/site_to_func.py', found[0])
        function = re.search(r'func (0x[0-9A-Fa-f]+)', mapped)
        if not function:
            continue
        start = int(function.group(1), 16)
        path = os.path.join(TEMP, 'r1372_%s.c' % name)
        run('analysis/dump_dec.py', hex(start), path)
        code = io.open(path, encoding='utf-8', errors='replace').read()
        offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
        decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
        strings = [line.split("'", 2)[1] for line in decoded.splitlines()
                   if ' str ' in line and "'" in line]
        print('      %#x  %d literals: %s' % (start, len(strings),
                                             ' | '.join(s[:30] for s in strings[:14])))
