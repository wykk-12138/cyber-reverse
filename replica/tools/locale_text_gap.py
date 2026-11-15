import io, os, re, sys

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
SRC = r'D:\projects\cyber-reverse\replica\src'

raw = io.open(POOL, encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"([A-Z][\w.]*\.[\w.]+)":\s*"([^"\n]{1,80})"', raw)))
corpus = []
for dp, _d, fns in os.walk(SRC):
    for fn in fns:
        if fn.endswith('.cs'):
            corpus.append(io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read())
text = '\n'.join(corpus)

area = sys.argv[1] if len(sys.argv) > 1 else None
rows = [(k, v) for k, v in pairs if area is None or k.split('.')[0].lower() == area.lower()]
absent = [(k, v) for k, v in rows if v and v not in text]
print('%s: %d key/value pairs, %d values not present in the source' % (area or 'all', len(rows), len(absent)))
for k, v in absent[:24]:
    print('   %-46s %s' % (k, v))
