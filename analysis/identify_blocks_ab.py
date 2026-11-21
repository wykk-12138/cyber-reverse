"""One sender from each of blocks A and B: which host do they carry?"""

import io
import os
import re
import subprocess
import sys

TARGETS = {
    'A_cartApiObjectCreate': 0x140D1B380,
    'B_getCart': 0x140E55F90,
}
TEMP = os.environ.get('TEMP', '.')

for label, address in TARGETS.items():
    path = os.path.join(TEMP, 'r1348_%s.c' % label)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(address), path],
                   capture_output=True, text=True)
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout
    strings = [line.split("'", 2)[1] for line in out.splitlines() if ' str ' in line and "'" in line]
    hosts = [s for s in strings if 'http' in s or ('/' in s and '.' in s)]
    print('=== %s  %#x  (%d literals)' % (label, address, len(strings)))
    print('    hosts/paths: %s' % hosts[:6])
    print('    literals:    %s' % ' | '.join(strings[:14]))
    print()
