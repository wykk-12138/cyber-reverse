"""Which URL does each cart mutation's sender post to?

R1320/R1321 wired createEmptyCart, addProductsToCart and SubmitOrder to <origin>/graphql and labelled it an
inference. R1333 then found /cartApi/checkout on the store's themeapis subdomain, which put that inference in
doubt. This reads the three senders and answers it.

Usage: python analysis/cart_senders.py
"""

import os
import re
import subprocess
import sys

SENDERS = {
    'createEmptyCart': '0x1409590B0',
    'addProductsToCart': '0x140958480',
    'submitOrder': '0x140891F70',
}

TEMP = os.environ.get('TEMP', '.')


def run(args):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True).stdout


for name, address in SENDERS.items():
    path = os.path.join(TEMP, 'r1337_%s.c' % name)
    run(['analysis/dump_dec.py', address, path])
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    print('=== %s  %s  %d literals' % (name, address, len(offsets)))
    if not offsets:
        print('   (no literals decoded)')
        continue
    decoded = run(['analysis/names_at.py'] + ['0x' + offset for offset in offsets])
    for line in decoded.splitlines():
        if ' str ' in line:
            print('   ' + line.strip()[:110])
    print()
