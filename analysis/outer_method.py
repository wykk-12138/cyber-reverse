"""Async senders hide their caller one level up: find who starts the state machine.

The six unattributed operations all decompile to state-machine MoveNext bodies, where the URL lives in fields the
caller filled in. Five of the call sites for getCart's MoveNext are at 0x1422A07A4 and 0x1428EA9E7/ADA — the second
pair is a table of some kind, the first is code. This reads the code caller, which is the method that built the
state machine and therefore holds the URL.
"""

import io
import os
import re
import subprocess
import sys

SITES = [0x1422A07A4, 0x1428EA9E7, 0x1428EAADA]
TEMP = os.environ.get('TEMP', '.')

for site in SITES:
    out = subprocess.run([sys.executable, 'analysis/site_to_func.py', hex(site)],
                         capture_output=True, text=True).stdout
    match = re.search(r'func (0x[0-9A-Fa-f]+)', out)
    print('site %#x -> %s' % (site, match.group(1) if match else 'no function'))
    if not match:
        continue

    function = int(match.group(1), 16)
    path = os.path.join(TEMP, 'r1353_outer_%x.c' % function)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(function), path],
                   capture_output=True, text=True)
    if not os.path.exists(path):
        continue
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                             capture_output=True, text=True).stdout
    strings = [line.strip()[:90] for line in decoded.splitlines() if ' str ' in line]
    print('   %d literals' % len(strings))
    for line in strings[:14]:
        print('     ' + line)
    print()
