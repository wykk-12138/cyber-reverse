"""What does the function that sets all three browser-surface headers carry?"""

import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

code = io.open(r'C:\Users\wykk\AppData\Local\Temp\r1379_a.c', encoding='utf-8', errors='replace').read()
offsets = sorted(set(re.findall(r'&?off_([0-9A-F]{9})', code)))
decoded = subprocess.run([sys.executable, 'analysis/names_at.py'] + ['0x' + o for o in offsets],
                         capture_output=True, text=True).stdout

strings = [line.split("'", 2)[1] for line in decoded.splitlines() if ' str ' in line and "'" in line]
print('%d literals:' % len(strings))
for value in strings:
    print('    %s' % value[:110])

print()
print('pseudocode, first 60 lines:')
for line in code.splitlines()[:60]:
    print('  ' + line[:118])
