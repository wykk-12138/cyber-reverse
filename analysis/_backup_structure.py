import io, os, glob, json
A = os.path.expandvars(r"%APPDATA%\Cybersole")
p = sorted(glob.glob(os.path.join(A,'Backups','*.cyb')))[-1]
d = json.loads(io.open(p, encoding='utf-8', errors='replace').read())
print('backup:', os.path.basename(p))
for k, v in d.items():
    if isinstance(v, list):
        inner = list(v[0].keys()) if v and isinstance(v[0], dict) else None
        print('%-22s list[%d] %s' % (k, len(v), inner if inner else ''))
    elif isinstance(v, dict):
        print('%-22s dict keys: %s' % (k, ', '.join(list(v)[:12])))
