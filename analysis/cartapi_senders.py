"""Decode the senders of the three cartApi-family documents."""

import os
import re
import subprocess
import sys

PAIRS = {
    'addLineItem': '0x140B56880',
    'addDiscountCode': '0x140B585B0',
    'cartApiObjectCreate': '0x140D1B380',
}

TEMP = os.environ.get('TEMP', '.')

for name, address in PAIRS.items():
    path = os.path.join(TEMP, 'r1337b_%s.c' % name)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', address, path],
                   capture_output=True, text=True)
    text = open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    print('=== %s  %s  %d literals' % (name, address, len(offsets)))
    if not offsets:
        continue
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if ' str ' in line:
            print('   ' + line.strip()[:110])
    print()
