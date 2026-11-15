import io, re, collections
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
paths = {t for t in rows if re.match(r'^/[a-zA-Z0-9_\-/{}.$*]+(/[a-zA-Z0-9_\-/{}.$*]+)+$', t) or re.match(r'^/[a-z0-9]+', t) and 8 < len(t) < 90 and ' ' not in t}
print('path-shaped strings in pool:', len(paths))
tops = collections.Counter(p.split('/')[1] for p in paths)
print('top first segments:', tops.most_common(10))
