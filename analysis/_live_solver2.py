import io, json, os
p = os.path.expandvars(r"%APPDATA%\Cybersole\solvers.json")
d = json.loads(io.open(p, encoding='utf-8-sig', errors='replace').read())
print('type:', type(d).__name__, 'len', len(d))
first = d[0]
print('first element type:', type(first).__name__, 'keys:', list(first.keys()) if isinstance(first, dict) else first)
inner = first.get('solvers') if isinstance(first, dict) else None
print('inner type:', type(inner).__name__, 'len', len(inner) if hasattr(inner, '__len__') else '-')
if isinstance(inner, list) and inner:
    print('solver object keys:', ', '.join(inner[0].keys()))
    st = inner[0].get('settings') or {}
    print('settings keys (%d): %s' % (len(st), ', '.join(list(st)[:24])))
