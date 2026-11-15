import io, os, json, glob
A = os.path.expandvars(r"%APPDATA%\Cybersole")
raw = io.open(sorted(glob.glob(os.path.join(A,'Backups','*.cyb')))[-1], encoding='utf-8', errors='replace').read()
d = json.loads(raw)
print('backup top-level keys (%d):' % len(d))
for k, v in d.items():
    print('   %-24s %s%s' % (k, type(v).__name__, (' len=%d' % len(v)) if hasattr(v, '__len__') and not isinstance(v, (str,int,float,bool)) else ''))
