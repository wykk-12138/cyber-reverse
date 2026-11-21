"""What functions reference the Warhammer GraphQL endpoint, and what do they send?

R1339 established the technique on Highsnobiety: one host string, one reference list, one store's whole HTTP
surface. This applies it to a store the replica already implements, to answer a different question — are the steps
it implements the same set the image has?

The scan has to try both addresses. The Warhammer endpoint is referenced through the object header (0x147054A60),
which is what §2.7d predicts; Highsnobiety's senders referenced the characters directly. One of the two always
works, and only trying both makes "no reference" a statement rather than a guess.

Usage: python analysis/warhammer_surface.py
"""
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

HOST = 'https://api.prod.warhammer.com/graphql'
CHARS_VA = 0x147054A6C
TEMP = os.environ.get('TEMP', '.')


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True).stdout


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


print('host: %s' % HOST)
for label, address in (('object header', CHARS_VA - 12), ('characters', CHARS_VA)):
    out = run(['analysis/disp32_scan_any.py', hex(address)])
    sites = re.findall(r'VA (0x[0-9A-Fa-f]+)', out)[1:]
    print('  %-14s %#x -> %d site(s)' % (label, address, len(sites)))

sites = re.findall(r'VA (0x[0-9A-Fa-f]+)', run(['analysis/disp32_scan_any.py', hex(CHARS_VA - 12)]))[1:]
functions = []
for site in sites:
    match = re.search(r'func (0x[0-9A-Fa-f]+)\.\.', run(['analysis/site_to_func.py', site]))
    if match:
        functions.append(int(match.group(1), 16))

print()
for address in sorted(set(functions)):
    path = os.path.join(TEMP, 'r1340_w_%x.c' % address)
    run(['analysis/dump_dec.py', hex(address), path])
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run(['analysis/names_at.py'] + ['0x' + offset for offset in offsets]).splitlines()
    strings = []
    for line in decoded:
        if ' str ' in line and "'" in line:
            strings.append(line.split("'", 2)[1])
    print('%#x  %s' % (address, ' | '.join(strings[:12])))
