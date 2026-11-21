"""Read the function that references cartLineItemSet: does it carry the Shop app host?"""

import io
import os
import re
import subprocess
import sys

ADDRESS = 0x140D11730
TEMP = os.environ.get('TEMP', '.')
path = os.path.join(TEMP, 'r1355_clis.c')

subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(ADDRESS), path], capture_output=True, text=True)
text = io.open(path, encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
print('%#x  %d literal offsets  (%d lines)' % (ADDRESS, len(offsets), len(text.splitlines())))

out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                     capture_output=True, text=True).stdout
for line in out.splitlines():
    if ' str ' in line:
        print('   ' + line.strip()[:110])
