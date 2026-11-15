import io, json, re
# replica locale keys
en = json.load(io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json', encoding='utf-8'))
def keys(d, prefix=''):
    out = set()
    for k, v in d.items():
        out.add(prefix + k)
        if isinstance(v, dict): out |= keys(v, prefix + k + '.')
    return out
rk = keys(en)
print('replica en keys:', len(rk))

# pool keys: dotted identifiers that are *used* as locale keys (heuristic: appear also in another language file)
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
pk = {t for t in rows if re.match(r'^[A-Z][A-Za-z0-9]*(\.[A-Za-z0-9]+){1,4}$', t) and len(t) < 80}
print('pool locale-shaped keys:', len(pk))
missing = sorted(k for k in pk if k not in rk)
print('pool keys not in replica en:', len(missing))
for k in missing[:15]: print('   -', k)
