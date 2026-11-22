"""Read every literal the address sender references, so the AddressInput shape rests on one function."""

import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

code = io.open(r'C:\Users\wykk\AppData\Local\Temp\r1372_a.c', encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
print('literals referenced: %d' % len(offsets))

decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout

for line in decoded.splitlines():
    if ' str ' in line:
        print(line.strip())
    elif ' raw ' in line:
        print(line.strip()[:120])
