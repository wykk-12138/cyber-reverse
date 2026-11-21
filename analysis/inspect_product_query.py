"""The Product query's sender: what does it post, and where?"""

import io
import os
import re
import subprocess
import sys

ADDRESS = 0x140E1BAB0
TEMP = os.environ.get('TEMP', '.')
path = os.path.join(TEMP, 'r1345.c')

subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(ADDRESS), path], capture_output=True, text=True)
text = io.open(path, encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
print('%#x  %d literal offsets' % (ADDRESS, len(offsets)))

out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                     capture_output=True, text=True).stdout
for line in out.splitlines():
    if ' str ' in line:
        print('   ' + line.strip()[:112])
