"""Full literal list for the GetCartCookie handler, plus the header set it builds."""

import io
import os
import re
import subprocess
import sys

ADDRESS = 0x14088BB80
TEMP = os.environ.get('TEMP', '.')
path = os.path.join(TEMP, 'r1357_cookie.c')

subprocess.run([sys.executable, 'analysis/dump_dec.py', hex(ADDRESS), path], capture_output=True, text=True)
text = io.open(path, encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', text)))
print('%#x  %d literals  (%d lines of pseudocode)' % (ADDRESS, len(offsets), len(text.splitlines())))

out = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                     capture_output=True, text=True).stdout
for line in out.splitlines():
    if ' str ' in line:
        print('   ' + line.strip()[:150])

# Where do the literals get used? Show the call-shape lines.
print()
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith('v') and ('sub_1430' in stripped or 'off_' in stripped):
        print('   | ' + stripped[:130])
