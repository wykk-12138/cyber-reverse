import json, urllib.request

def call(method, params=None, path='/mcp'):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []}).encode()
    req = urllib.request.Request('http://127.0.0.1:13337' + path, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))

for m in ('get_metadata', 'server_health'):
    try:
        res = call(m)
        txt = json.dumps(res, ensure_ascii=False)
        print(m, '->', txt[:400])
    except Exception as e:
        print(m, 'FAILED:', type(e).__name__, e)
