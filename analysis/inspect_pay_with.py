"""Two senders reference PayWithQuery — read both."""

import io
import os
import re
import subprocess
import sys

FUNCS = {
    'a': 0x140F4C550,
    'b': 0x14110D030,
}

TEMP = os.environ.get('TEMP', '.')

for label, address in FUNCS.items():
    path = os.path.join(TEMP, 'r1343_%s.c' % label)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(address), path],
                   capture_output=True, text=True)
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    print('=== %s  %#x  (%d literal offsets)' % (label, address, len(offsets)))
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if ' str ' in line:
            print('   ' + line.strip()[:110])
    print()
