import io, os, json, re

A = os.path.expandvars(r"%APPDATA%\Cybersole")
SRC = r"D:\projects\cyber-reverse\replica\src"

def live(file, path=()):
    p = os.path.join(A, file)
    raw = io.open(p, encoding='utf-8-sig', errors='replace').read()
    if not raw.strip(): return None
    d = json.loads(raw)
    for step in path:
        d = d[step]
    return d

def keys(x):
    if isinstance(x, list):
        return list(x[0].keys()) if x and isinstance(x[0], dict) else ('list[%d]' % len(x) if isinstance(x, list) else x)
    if isinstance(x, dict):
        return list(x.keys())
    return type(x).__name__

for f, path in [('accounts.json', ()), ('billing.json', ()), ('proxies.json', ()),
                ('analytics.json', ()), ('smartActions.json', ()), ('smartActionUtilities.json', ())]:
    d = live(f, path)
    print('%-26s %s' % (f, keys(d)))

print()
b = live('billing.json')
if isinstance(b, list) and b:
    print('billing[0]:', json.dumps(b[0])[:200])
p = live('proxies.json')
if isinstance(p, list) and p:
    print('proxies[0] keys:', list(p[0].keys()))
    pr = p[0].get('proxies')
    if isinstance(pr, list) and pr and isinstance(pr[0], dict):
        print('proxy entry keys:', list(pr[0].keys()))
