import io, re, glob
cookies = {}
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'Cookies(?:\.TryGetValue)?\(\s*"([A-Za-z0-9_\-\.]+)"', t):
        cookies.setdefault(m.group(1), set()).add(f.split('replica\\')[-1].replace('\\','/'))
    for m in re.finditer(r'Cookies\[\s*"([A-Za-z0-9_\-\.]+)"\s*\]\s*=', t):
        cookies.setdefault(m.group(1), set()).add(f.split('replica\\')[-1].replace('\\','/'))
print('replica cookie names referenced:', len(cookies))
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (p.match(l) for l in lines) if m}
lower = {x.lower(): x for x in pool}
hit, miss = [], []
for c in sorted(cookies):
    if c in pool or c.lower() in lower: hit.append(c)
    else: miss.append(c)
print('in pool: %d   not in pool: %d' % (len(hit), len(miss)))
for c in miss:
    print('   %-28s %s' % (c, sorted(cookies[c])[0]))
