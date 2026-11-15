import io, json, os
p = os.path.expandvars(r"%APPDATA%\Cybersole\settings.json")
raw = io.open(p, encoding='utf-8-sig', errors='replace').read()
print('bytes:', len(raw))
try:
    d = json.loads(raw)
except Exception as e:
    print('parse error:', e)
    print(raw[:600])
    raise SystemExit
def walk(o, prefix=''):
    if isinstance(o, dict):
        for k, v in o.items():
            key = prefix + k
            if isinstance(v, (dict, list)):
                print('%-46s %s' % (key, type(v).__name__))
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    walk(v[0], key + '[].')
                elif isinstance(v, dict):
                    walk(v, key + '.')
            else:
                print('%-46s %s' % (key, type(v).__name__))
walk(d)
