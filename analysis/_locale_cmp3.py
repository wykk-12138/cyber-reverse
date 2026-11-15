import io, json, re
en = json.load(io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json', encoding='utf-8'))
def keys(d, prefix=''):
    out = set()
    for k, v in d.items():
        out.add(prefix + k)
        if isinstance(v, dict): out |= keys(v, prefix + k + '.')
    return out
rk = keys(en)
tops = {k.split('.')[0] for k in rk}
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
pk = {t for t in rows if re.match(r'^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z0-9]+){1,4}$', t) and len(t) < 80}
missing = sorted(k for k in pk if k.split('.')[0] in tops and k not in rk)
for k in missing:
    longer = sorted(x for x in pk if x.startswith(k + '.'))
    sim = sorted(x for x in rk if x.split('.')[0] == k.split('.')[0] and k.split('.')[-1].lower() in x.lower())
    print('%-24s  更长键:%s  复刻件相近:%s' % (k, longer[:2] or '-', sim[:2] or '-'))
