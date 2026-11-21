"""Three senders, three families: which host does each carry?"""

import io
import os
import re
import subprocess
import sys

TARGETS = {
    'getProductDetails': 0x140C81880,
    'saveAddress': 0x140E5AE30,
    'maintainShippingGroups': 0x140E58F00,
}
TEMP = os.environ.get('TEMP', '.')

for label, address in TARGETS.items():
    path = os.path.join(TEMP, 'r1351_%s.c' % label)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(address), path],
                   capture_output=True, text=True)
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout
    strings = [line.split("'", 2)[1] for line in out.splitlines() if ' str ' in line and "'" in line]
    hosts = [s for s in strings if 'http' in s or s.endswith('graphql') or s.startswith('api/')]
    print('%-24s %#x' % (label, address))
    print('   hosts: %s' % hosts[:4])
    print('   literals: %s' % ' | '.join(strings[:12]))
    print()
