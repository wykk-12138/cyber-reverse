import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [(m.group(1), m.group(2)) for m in (pat.match(l) for l in lines) if m]
# print every row whose address is in the 0x0320b000..0x0320d000 window, to see the layout
sel = [(a, t) for a, t in rows if 0x0320b000 <= int(a, 16) <= 0x0320c800]
print('rows in 0x0320b000..0x0320c800:', len(sel))
for a, t in sel[:40]:
    print(' ', a, t[:120])
