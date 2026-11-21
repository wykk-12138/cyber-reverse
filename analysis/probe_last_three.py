"""The last three: what do their handlers carry, and does either belong to a family I already have?

    updateShipAddress           140 chars, $address        handler sub_14088C350
    updateMyPaymentWithActions  401 chars, actions/id/version  handler sub_140E55A00
    SignInAsGuest               453 chars                  handler sub_140CFF770 (accessToken/authPayload, no host)

The first two matter because both sit near families that are already implemented: 0x14088xxxx is where queries go by
hash, and 0x140E5xxxx is the session family. If either handler names a hash header or the /graphql path, the answer is
immediate.

Usage: python analysis/probe_last_three.py
"""
import io
import os
import re
import subprocess
import sys

HANDLERS = {
    'updateShipAddress': 0x14088C350,
    'updateMyPaymentWithActions': 0x140E55A00,
    'SignInAsGuest': 0x140CFF770,
}
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for label, address in HANDLERS.items():
    path = os.path.join(TEMP, 'r1364_%s.c' % label)
    run('analysis/dump_dec.py', hex(address), path)
    text = io.open(path, encoding='utf-8', errors='replace').read() if os.path.exists(path) else ''
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]

    signals = []
    if any('x-graphql-hash' in s for s in strings): signals.append('hash header')
    if any(s.startswith('https://') or s.endswith('/graphql') or s == 'api/graphql' for s in strings):
        signals.append('path')
    if any('window.location' in s or 'cookie' in s.lower() for s in strings): signals.append('cookie')

    print('=== %-26s %#x  %d literals  signals=%s' % (label, address, len(strings), signals or ['none']))
    for value in strings[:16]:
        print('    %s' % value[:100])
    print()
