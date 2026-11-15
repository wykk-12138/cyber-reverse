import re
lines = open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for i, ln in enumerate(lines, 1):
    if not (158471 <= i <= 158521): continue
    m = pat.match(ln)
    if m: print(f'{i:7d} {m.group(1)}  {m.group(2)[:175]}')
