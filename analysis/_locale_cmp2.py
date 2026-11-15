import io, json, re, collections
en = json.load(io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json', encoding='utf-8'))
def keys(d, prefix=''):
    out = set()
    for k, v in d.items():
        out.add(prefix + k)
        if isinstance(v, dict): out |= keys(v, prefix + k + '.')
    return out
rk = keys(en)
tops = {k.split('.')[0] for k in rk}
print('replica top-level groups:', len(tops))

lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
pk = {t for t in rows if re.match(r'^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z0-9]+){1,4}$', t) and len(t) < 80}
same_top = {k for k in pk if k.split('.')[0] in tops}
missing = sorted(k for k in same_top if k not in rk)
print('pool keys under replica\'s own groups:', len(same_top), ' missing:', len(missing))
by_group = collections.Counter(k.split('.')[0] for k in missing)
print('top missing groups:', by_group.most_common(8))
for k in missing[:12]: print('   -', k)
