"""Two promising blocks: do they carry a host, a path, or nothing?

    GetCart 3520, GetCartCookie 74, GetProductInventory 490     at 0x14711efc4
    CartLineItemSet 1255, CreditCard 2867                       at 0x1470ce874

GetCartCookie at 74 characters is short enough to read outright, and CartLineItemSet is the name Storefront gives to
its cart-lines mutation, so both blocks are worth one sender each before deciding anything.

Usage: python analysis/scan_two_blocks.py
"""
import io
import os
import re
import subprocess
import sys

DOCUMENTS = {
    'GetCart': 0x14711EFC4,
    'GetCartCookie': 0x147120B5C,
    'GetProductInventory': 0x147120C0C,
    'CartLineItemSet': 0x1470CE874,
    'CreditCard': 0x1470CF934,
}
TEMP = os.environ.get('TEMP', '.')


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True, text=True).stdout


for name, address in DOCUMENTS.items():
    sites = run('analysis/disp32_scan_any.py', hex(address - 12))
    first = re.search(r'VA (0x[0-9A-Fa-f]+)\n', sites)
    if not first:
        print('%-22s no code reference' % name)
        continue

    function = re.search(r'func (0x[0-9A-Fa-f]+)', run('analysis/site_to_func.py', first.group(1)))
    if not function:
        print('%-22s site %s in no function' % (name, first.group(1)))
        continue

    start = int(function.group(1), 16)
    path = os.path.join(TEMP, 'r1355_%s.c' % name)
    run('analysis/dump_dec.py', hex(start), path)
    text = io.open(path, encoding='utf-8', errors='replace').read() if os.path.exists(path) else ''
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = run('analysis/names_at.py', *['0x' + o for o in offsets])
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]

    hosts = [s for s in strings if 'http' in s or s.endswith('graphql.json') or s.endswith('/graphql')]
    paths = [s for s in strings if s not in hosts and (('/' in s and len(s) > 8) or '?' in s)]
    print('%-22s %#x  host=%s path=%s' % (name, start, hosts[:2], paths[:3]))
    print('   literals: %s' % ' | '.join(strings[:10]))
