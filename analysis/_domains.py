import io, re, collections
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
urls = collections.defaultdict(set)
for r in rows:
    for m in re.finditer(r'https?://([a-z0-9.\-]+\.[a-z]{2,})', r):
        urls[m.group(1)].add(r[:160])
print('domains in the pool:', len(urls))
for d in ('www.goat.com','www.popmart.com','www.farfetch.com','www.magento','api.magento','www.scheels.com','www.hbx.com'):
    hits = urls.get(d, set())
    if hits:
        print('==', d, len(hits))
        for h in list(hits)[:4]: print('    ', h[:120])
