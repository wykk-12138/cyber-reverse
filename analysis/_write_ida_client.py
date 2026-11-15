import io
src = r'''"""Minimal MCP client for the IDA plugin's HTTP endpoint (127.0.0.1:13337/mcp).

R428: DSH's `ida` MCP proxy kept dying, but the plugin itself speaks MCP over HTTP. This client talks to the plugin
directly, so decompilation work no longer depends on the proxy being alive.

Usage:
    python analysis/ida.py health
    python analysis/ida.py tools
    python analysis/ida.py funcs TaskView
    python analysis/ida.py dec 0x140001000 [--lines N]
    python analysis/ida.py xrefs <name-or-addr>
    python analysis/ida.py str "Monitor\\.Tab"
"""
import json, sys, urllib.request

URL = 'http://127.0.0.1:13337/mcp'
_id = [0]


def _rpc(method, params=None, timeout=180):
    _id[0] += 1
    body = json.dumps({'jsonrpc': '2.0', 'id': _id[0], 'method': method, 'params': params or {}}).encode()
    req = urllib.request.Request(URL, data=body, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


def initialize():
    _rpc('initialize', {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'cyber-reverse', 'version': '1'}})


def call(tool, args=None, timeout=180):
    res = _rpc('tools/call', {'name': tool, 'arguments': args or {}}, timeout=timeout)
    if 'error' in res:
        return 'ERROR: ' + json.dumps(res['error'], ensure_ascii=False)
    out = res.get('result', {})
    texts = [c.get('text', '') for c in (out.get('content') or []) if isinstance(c, dict)]
    text = '\n'.join(texts) if texts else json.dumps(out, ensure_ascii=False)
    return text


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    initialize()

    if cmd == 'health':
        print(call('server_health'))
    elif cmd == 'tools':
        tools = json.loads(_rpc('tools/list', {})['result'] and json.dumps(_rpc('tools/list', {})))
        for t in tools['result']['tools']:
            print('%-18s %s' % (t['name'], (t.get('description') or '').split('\n')[0][:90]))
    elif cmd == 'funcs':
        print(call('func_query', {'queries': [{'name_contains': rest[0]}]}))
    elif cmd == 'dec':
        args = {'addr': rest[0]}
        if '--lines' in rest:
            args['max_lines'] = int(rest[rest.index('--lines') + 1])
        print(call('decompile', args))
    elif cmd == 'dis':
        print(call('disasm', {'addr': rest[0]}))
    elif cmd == 'xrefs':
        print(call('xrefs_to', {'addrs': [rest[0]]}))
    elif cmd == 'str':
        print(call('find_regex', {'pattern': rest[0], 'limit': 40}))
    else:
        print('unknown command:', cmd)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
'''
io.open(r"D:\projects\cyber-reverse\analysis\ida.py", 'w', encoding='utf-8', newline='').write(src)
print('analysis/ida.py written')
