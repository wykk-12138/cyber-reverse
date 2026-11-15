import io, re, glob
hdr = {}
pat = re.compile(r'"((?:[A-Za-z0-9]+-)+[A-Za-z0-9]+)"')
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    for m in pat.finditer(t):
        h = m.group(1)
        if re.match(r'^(X-|Sec-|Accept|Content|User-Agent|Referer|Origin|Cookie|Authorization|Cache|If-|Access-|DNT|Pragma|Connection|Host|TE|Upgrade|Via|Warning|Vary|Allow|Age|Date|ETag|Expires|Last-|Location|Retry-|Server|Set-|Transfer-|Www-)', h):
            hdr.setdefault(h, set()).add(f.split('replica\\')[-1].replace('\\','/'))
print('replica header-like literals:', len(hdr))

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p2 = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (p2.match(l) for l in lines) if m}
hit = sorted(h for h in hdr if h in pool)
miss = sorted(h for h in hdr if h not in pool)
print('in pool: %d   not in pool: %d' % (len(hit), len(miss)))
for h in miss[:20]:
    print('   %-34s %s' % (h, sorted(hdr[h])[0]))
