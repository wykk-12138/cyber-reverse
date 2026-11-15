import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
frags = ['identificationSignature','_identificationSignature','sec-fetch','com.nike','identification']
seen = set()
for ln in lines:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if any(f in t for f in frags):
        key = t[:120]
        if key in seen: continue
        seen.add(key)
        print(m.group(1), t[:150])
