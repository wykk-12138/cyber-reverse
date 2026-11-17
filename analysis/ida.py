"""Minimal MCP client for the IDA plugin's HTTP endpoint (127.0.0.1:13337/mcp).

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
        # R817: the limit was hard-coded to 40. That made every count from this tool silently capped: `str kasada`,
        # `str cloudflare`, `str stripe` and `str myshopify` all returned exactly 40, which reads like a coincidence
        # and is not one. Zero and values below forty were still trustworthy, so the cap only corrupted counting, not
        # existence checks -- but it corrupted them invisibly, and R814's slug count had to be walked back because of
        # it. Pass --limit N to raise it.
        limit = 40
        if '--limit' in rest:
            limit = int(rest[rest.index('--limit') + 1])
        # R1075: the plugin answers with a key called `n`, which is how many strings came BACK, not how many matched.
        # R1067 established that by sweeping the limit, and R1073 then read a limit of 4 as a total of 4 anyway --
        # the fifth time here that a sample was read as a census. Writing it down did not stop it, so the interface is
        # fixed instead: `returned` says what arrived, `saturated` says whether the cap was hit, and `total` is a real
        # total only when the reply is unsaturated. A saturated result cannot be quoted as a count.
        raw = call('find_regex', {'pattern': rest[0], 'limit': limit})
        try:
            obj = json.loads(raw)
            hits = obj.get('matches') or []
            obj['returned'] = len(hits)
            obj['limit'] = limit
            obj['saturated'] = len(hits) >= limit
            obj['total'] = len(hits) if len(hits) < limit else 'at least %d (saturated -- raise --limit)' % len(hits)
            obj['n'] = obj.get('n', len(hits))
            print(json.dumps(obj))
        except Exception:
            print(raw)
    elif cmd == 'call':
        # generic passthrough: python analysis/ida.py call <tool> '<json args>'
        print(call(rest[0], json.loads(rest[1]) if len(rest) > 1 else {}))
    elif cmd == 'py':
        # IDAPython one-off: python analysis/ida.py py "<code>" [--timeout SECS]
        # R572: the default 180 s is too short for a loop over 321,244 functions; the caller may raise it.
        code = rest[0] if rest and rest[0] != '-' else sys.stdin.read()
        secs = 180
        if '--timeout' in rest:
            secs = int(rest[rest.index('--timeout') + 1])
            if code == rest[rest.index('--timeout') + 1]:
                code = sys.stdin.read()
        print(call('py_eval', {'code': code}, timeout=secs))
    else:
        print('unknown command:', cmd)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
