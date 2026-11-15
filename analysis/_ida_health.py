import io, json, sys, urllib.request

URL = 'http://127.0.0.1:13337/mcp'
_id = [0]

def rpc(method, params=None):
    _id[0] += 1
    body = json.dumps({'jsonrpc': '2.0', 'id': _id[0], 'method': method, 'params': params or {}}).encode()
    req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))

def call(tool, args=None):
    res = rpc('tools/call', {'name': tool, 'arguments': args or {}})
    if 'error' in res:
        return {'error': res['error']}
    out = res.get('result', {})
    content = out.get('content') or []
    texts = [c.get('text', '') for c in content if isinstance(c, dict)]
    return {'isError': out.get('isError', False), 'text': '\n'.join(texts) or json.dumps(out, ensure_ascii=False)[:2000]}

print(call('server_health'))
print('---- list_funcs Task* ----')
r = call('func_query', {'name_contains': 'TaskView'})
print(r.get('text', r)[:1500])
