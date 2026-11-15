import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(int(m.group(1), 16), m.group(2)) for m in (pat.match(l) for l in lines) if m]
for a, t in rows:
    if 0x034b23a5 <= a <= 0x034b23a5 + 0x40:
        print('0x%08x:' % a)
        print(repr(t))
