import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = []
for ln in lines:
    m = pat.match(ln)
    if m: rows.append((int(m.group(1),16), m.group(2)))
want = ('com.nike.', 'nike:', 'nike_android', 'snkrs', 'com.nike.commerce')
for a,t in rows:
    if any(w in t for w in want) and len(t) < 90:
        print(hex(a), t[:90])
