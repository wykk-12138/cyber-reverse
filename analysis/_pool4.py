import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for ln in lines:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if 'Settings.General.' in t and len(t) > 40 and (':' in t or '"' in t):
        print(m.group(1), t[:230])
