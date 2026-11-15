import io, json, os
p = os.path.expandvars(r"%APPDATA%\Cybersole\solvers.json")
d = json.loads(io.open(p, encoding='utf-8-sig', errors='replace').read())
s = d[0]
print('solver keys:', ', '.join(s.keys()))
st = s.get('settings') or {}
print('settings keys (%d): %s' % (len(st), ', '.join(st.keys())))
print()
print('sample values:', {k: st[k] for k in list(st)[:6]})
