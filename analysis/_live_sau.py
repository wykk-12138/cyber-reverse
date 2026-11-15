import io, os, json
A = os.path.expandvars(r"%APPDATA%\Cybersole")
for fn in ('smartActionUtilities.json', 'analytics.json'):
    p = os.path.join(A, fn)
    raw = io.open(p, encoding='utf-8-sig', errors='replace').read()
    print(fn, 'bytes', len(raw))
    d = json.loads(raw) if raw.strip() else None
    if isinstance(d, dict):
        print('   keys:', ', '.join(list(d)[:12]))
        for k, v in list(d.items())[:4]:
            if isinstance(v, dict): print('     %-16s -> %s' % (k, ', '.join(list(v)[:8])))
    elif isinstance(d, list):
        print('   list len', len(d))
