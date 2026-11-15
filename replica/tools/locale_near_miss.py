import io, os, re, sys, difflib

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
SRC = r'D:\projects\cyber-reverse\replica\src'
area = sys.argv[1] if len(sys.argv) > 1 else 'Settings'

raw = io.open(POOL, encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"([A-Z][\w.]*\.[\w.]+)":\s*"([^"\n]{8,70})"', raw)))
locale = [(k, v) for k, v in pairs if k.split('.')[0].lower() == area.lower()]

lits = set()
for dp, _d, fns in os.walk(SRC):
    for fn in fns:
        if fn.endswith('.cs'):
            t = io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
            lits.update(re.findall(r'"([^"\\\n]{8,70})"', t))
lits = {l for l in lits if not l.startswith('http') and '.' not in l.split()[0]}

near = []
for k, v in locale:
    if v in lits:
        continue
    best = max(lits, key=lambda l: difflib.SequenceMatcher(None, v.lower(), l.lower()).ratio(), default=None)
    if best is None:
        continue
    r = difflib.SequenceMatcher(None, v.lower(), best.lower()).ratio()
    if r >= 0.75:
        near.append((k, v, best, r))

print('%s: %d locale values, %d near-matches (ratio >= .75) that are NOT equal' % (area, len(locale), len(near)))
for k, v, best, r in near[:14]:
    print('   %.2f  %-44s locale=%-34s replica=%s' % (r, k, v, best))
