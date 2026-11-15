import json, urllib.request

URL = 'http://127.0.0.1:13337/mcp'
_id = [0]

def rpc(method, params=None):
    _id[0] += 1
    body = json.dumps({'jsonrpc': '2.0', 'id': _id[0], 'method': method, 'params': params or {}}).encode()
    req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))

init = rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'crs-probe', 'version': '1'}})
print('initialize ->', json.dumps(init.get('result', init), ensure_ascii=False)[:300])
tools = rpc('tools/list', {})
names = [t['name'] for t in tools.get('result', {}).get('tools', [])]
print('tools:', len(names))
print(', '.join(names[:40]))
