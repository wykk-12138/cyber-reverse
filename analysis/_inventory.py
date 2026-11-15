import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
decl = re.compile(r'^\s*const ([A-Z][A-Z0-9_]+) = (\[|\{|new Set\(|new Map\()')
rows = []
for i, ln in enumerate(src, 1):
    m = pat.match(ln)
    if not m: continue
    off = int(m.group(1), 16)
    text = ln[12:]
    d = decl.match(text)
    if d and 0x03c00000 <= off <= 0x03e00000:
        rows.append((i, off, d.group(1), d.group(2), len(text)))
print(f'{len(rows)} table declarations in the script region')
for i, off, name, kind, size in rows:
    print(f'{i:6d} {off:#010x} {name:26} {kind:8} line={size}')
