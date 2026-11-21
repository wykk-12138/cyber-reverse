"""What else lives beside the Product sender? A store's senders tend to sit together.

The Product query's own function builds "api/graphql" as a relative path — the host is not in it — so the store has
to be found another way. Its neighbours are the cheapest place to look: senders in this image are grouped by
feature, and a host a few functions away would name the store.
"""

import io
import os
import re
import subprocess
import sys

CENTER = 0x140E1BAB0
WINDOW = 6
TEMP = os.environ.get('TEMP', '.')

# Walk .pdata-adjacent functions by scanning a byte window around the sender for `lea` targets is expensive;
# instead read the functions the scanner already knows from nearby code references.
NEARBY = [0x140E1BAB0 + delta for delta in (-0x600, -0x300, 0x300, 0x600, 0x900)]

for address in NEARBY:
    out = subprocess.run([sys.executable, 'analysis/site_to_func.py', hex(address)],
                         capture_output=True, text=True).stdout
    match = re.search(r'func (0x[0-9A-Fa-f]+)', out)
    if not match:
        continue
    function = int(match.group(1), 16)
    path = os.path.join(TEMP, 'r1345_n_%x.c' % function)
    subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(function), path],
                   capture_output=True, text=True)
    if not os.path.exists(path):
        continue
    text = io.open(path, encoding='utf-8', errors='replace').read()
    offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
    if not offsets:
        continue
    decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                             capture_output=True, text=True).stdout
    strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]
    hosts = [s for s in strings if '.' in s and '/' in s]
    print('%#x  (%d literals)  hosts: %s' % (function, len(strings), hosts[:3]))
    if strings:
        print('    %s' % ' | '.join(strings[:8]))
