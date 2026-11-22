"""Print the themeapis sender's full literal list and the call it makes."""

import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

code = io.open(r'C:\Users\wykk\AppData\Local\Temp\r1373_140c32160.c', encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout

print('literals:')
for line in decoded.splitlines():
    if ' str ' in line:
        print('   ' + line.strip())

print()
print('pseudocode, first 90 lines:')
for line in code.splitlines()[:90]:
    print(line[:120])
