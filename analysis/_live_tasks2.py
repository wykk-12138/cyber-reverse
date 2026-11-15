import io, json, os
p = os.path.expandvars(r"%APPDATA%\Cybersole\tasks.json")
d = json.loads(io.open(p, encoding='utf-8-sig', errors='replace').read())
g = d[0]
print('group keys:', ', '.join(g.keys()))
print()
t = (g.get('tasks') or [{}])[0]
print('task keys:', ', '.join(t.keys()) if t else '(none)')
print()
for k in ('webhooks', 'tasks'):
    v = g.get(k)
    print(k, 'len', len(v) if isinstance(v, list) else v)
    if isinstance(v, list) and v and isinstance(v[0], dict):
        print('   first keys:', ', '.join(v[0].keys()))
