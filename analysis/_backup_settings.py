import io, os, glob, json
A = os.path.expandvars(r"%APPDATA%\Cybersole")
p = sorted(glob.glob(os.path.join(A,'Backups','*.cyb')))[-1]
d = json.loads(io.open(p, encoding='utf-8', errors='replace').read())
st = d['settings']
print('settings keys (%d):' % len(st))
print(', '.join(st.keys()))
print()
acc = d['accounts']
for k, v in acc.items():
    if isinstance(v, list):
        print('%-14s list[%d] %s' % (k, len(v), list(v[0].keys()) if v and isinstance(v[0], dict) else ''))
    elif isinstance(v, dict):
        print('%-14s dict %s' % (k, list(v.keys())[:8]))
print()
b = d['billing'][0]
print('billing[0] keys:', list(b.keys()), '| profiles:', len(b.get('profiles') or []))
print('analytics:', {k: type(v).__name__ for k, v in d['analytics'].items()})
