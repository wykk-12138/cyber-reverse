import io, json, os
p = os.path.expandvars(r"%APPDATA%\Cybersole\tasks.json")
raw = io.open(p, encoding='utf-8-sig', errors='replace').read()
print('bytes:', len(raw))
d = json.loads(raw)
print('top type:', type(d).__name__)
def keys_of(o, prefix=''):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            out.append(prefix + k + ' : ' + type(v).__name__)
            if isinstance(v, dict): out += keys_of(v, prefix + k + '.')
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                out.append(prefix + k + '[] first-object keys: ' + ', '.join(list(v[0].keys())[:14]))
    return out
if isinstance(d, list):
    print('list length:', len(d))
    if d: 
        print('first object keys:', ', '.join(d[0].keys()))
else:
    for line in keys_of(d): print('   ', line)
