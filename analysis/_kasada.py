import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
want = ('149e9513', '/ips.js', '/fp?x-kpsdk', '/prop.json', 'x-kpsdk-v', 'x-kpsdk-cd', 'x-kpsdk-ct')
seen = set()
for ln in src:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if any(w in t for w in want) and t not in seen:
        seen.add(t)
        print(f'{m.group(1)}  {t[:150]}')
