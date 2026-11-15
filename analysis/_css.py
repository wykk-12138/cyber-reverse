import re
lines = open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for i, ln in enumerate(lines, 1):
    if not (158576 <= i <= 158606): continue
    m = pat.match(ln)
    if m:
        t = m.group(2)
        indent = len(t) - len(t.lstrip())
        if indent >= 4:
            print(f'{i:7d} ind={indent:2d} {t[:150]}')
