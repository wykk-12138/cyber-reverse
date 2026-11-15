import io, re
lines = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (pat.match(l) for l in lines) if m]
keys = [t for t in rows if re.match(r'^[A-Z][A-Za-z0-9]*(\.[A-Za-z0-9]+){1,4}$', t)]
for pref in ('SmartActions.Filter', 'SmartActions.Action', 'Profiles.Csv', 'Profile.Csv', 'Accounts.Csv'):
    hits = [k for k in keys if k.startswith(pref)]
    print('==', pref, len(hits))
    for k in hits[:8]:
        print('   ', k)
