"""What does the ProductDetails sender carry?"""

import io
import os
import re
import subprocess
import sys

TEMP = os.environ.get('TEMP', '.')
path = os.path.join(TEMP, 'r1342.c')
text = io.open(path, encoding='utf-8', errors='replace').read()

offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
print('literal offsets: %d' % len(offsets))

out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                     capture_output=True, text=True).stdout
for line in out.splitlines():
    if ' str ' in line:
        print('   ' + line.strip()[:120])
    elif ' raw ' in line:
        print('   ' + line.strip()[:70] + '  (candidate object header)')
