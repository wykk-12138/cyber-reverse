import io, json, os
A = os.path.expandvars(r"%APPDATA%\Cybersole")
def show(fn, path=()):
    p = os.path.join(A, fn)
    d = json.loads(io.open(p, encoding='utf-8-sig', errors='replace').read())
    for step in path:
        if isinstance(d, list): d = d[0]
        d = d[step] if not isinstance(d, list) else (d[0] if d else None)
    if isinstance(d, list): d = d[0] if d else None
    if isinstance(d, dict):
        print('%-22s %s -> %s' % (fn, '/'.join(path) or '(root)', ', '.join(d.keys())))
    else:
        print('%-22s %s -> %s' % (fn, '/'.join(path) or '(root)', type(d).__name__))

show('solvers.json', ())
show('solvers.json', ('solvers',))
show('billing.json', ('profiles',))
show('accounts.json', ('accountGroups',))
show('accounts.json', ('payPal',))
show('accounts.json', ('google',))
show('accounts.json', ('imap',))
show('proxies.json', ('proxies',))
show('smartActions.json', ('actions',))
show('smartActions.json', ('templates',))
