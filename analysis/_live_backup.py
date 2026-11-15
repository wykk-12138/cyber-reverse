import io, os, json, glob
A = os.path.expandvars(r"%APPDATA%\Cybersole")
cyb = sorted(glob.glob(os.path.join(A, 'Backups', '*.cyb')))
print('backups:', len(cyb))
raw = io.open(cyb[-1], 'rb').read()
print('first 32 bytes:', raw[:32])
print('looks like zip:', raw[:2] == b'PK')
try:
    print('as text head:', raw[:120].decode('utf-8', 'replace'))
except Exception as e:
    print('decode:', e)
print()
h = json.loads(io.open(os.path.join(A,'checkoutHistory.json'), encoding='utf-8-sig', errors='replace').read())
print('checkoutHistory type:', type(h).__name__)
if isinstance(h, list) and h:
    print('  len', len(h), 'first keys:', ', '.join(h[0].keys()))
elif isinstance(h, dict):
    print('  keys:', ', '.join(list(h)[:10]))
