"""The last seven block-A documents: find each sender, then look for a host or a path.

Seven documents remain in the range, all short, none sharing a signature:

    cartCreate 91, checkoutAsGuest 148, createCartByStore 421, createMyPayment 493,
    customerAccessTokenCreate 250, initiateCheckout 251, createCheckout 720

For each: scan for the code reference, map it to its function, decode the function's literals, and report whether
that function carries a host, a path, or neither. That single fact decides whether the document can be placed.

Usage: python analysis/scan_block_a_paths.py
"""
import io
import os
import re
import subprocess
import sys

DOCUMENTS = {
    'cartCreate': 0x1470F23FC,
    'checkoutAsGuest': 0x1470F24CC,
    'createCartByStore': 0x1470F32D4,
    'createCheckout': 0x1470F3634,
    'createMyPayment': 0x1470F3DC4,
    'customerAccessTokenCreate': 0x1470F41B4,
    'initiateCheckout': 0x1470F489C,
}
TEMP = os.environ.get('TEMP', '.')
results = {}


def run(script, *args):
    return subprocess.run([sys.executable, script] + list(args), capture_output=True, text=True).stdout


for name, address in DOCUMENTS.items():
    sites = run('analysis/disp32_scan_any.py', hex(address - 12))
    first = re.search(r'VA (0x[0-9A-Fa-f]+)\n', sites)
    if not first:
        results[name] = 'no code reference found'
        print('%-26s %s' % (name, results[name]))
        continue

    function = re.search(r'func (0x[0-9A-Fa-f]+)', run('analysis/site_to_func.py', first.group(1)))
    if not function:
        results[name] = 'site in no function'
        print('%-26s %s' % (name, results[name]))
        continue

    start = int(function.group(1), 16)
    path = os.path.join(TEMP, 'r1352_%s.c' % name)
    run('analysis/dump_dec.py', hex(start), path)
    if not os.path.exists(path):
        results[name] = 'no pseudocode'
        print('%-26s %s' % (name, results[name]))
        continue

    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]

    hosts = [s for s in strings if 'http' in s or s.endswith('graphql.json') or s.endswith('/graphql')]
    paths = [s for s in strings if ('/' in s or '?' in s) and s not in hosts and len(s) > 8]
    kind = 'host' if hosts else ('path' if paths else 'neither')
    results[name] = kind
    print('%-26s %#x  %-7s hosts=%s paths=%s' % (name, start, kind, hosts[:2], paths[:3]))

print()
print('host:', sum(1 for v in results.values() if v == 'host'))
print('path:', sum(1 for v in results.values() if v == 'path'))
print('neither:', sum(1 for v in results.values() if v == 'neither'))
print('other:', [k for k, v in results.items() if v not in ('host', 'path', 'neither')])
