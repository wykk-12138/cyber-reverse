import json, os, subprocess
node = r"D:\tools\node24\node-v24.22.1-win-x64\node.exe"
script = r"D:\tools\rea-agents\node_modules\rea-agents\scripts\rea.mjs"
env = {**os.environ, "PATH": os.path.dirname(node) + os.pathsep + os.environ["PATH"]}
p = subprocess.Popen([node, script, "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                     cwd=r"D:\tools\rea-agents", bufsize=1, env=env)
def send(i, m, params=None):
    p.stdin.write(json.dumps({"jsonrpc":"2.0","id":i,"method":m,"params":params or {}}) + "\n"); p.stdin.flush()
def call(tool, args, i):
    send(i, "tools/call", {"name": tool, "arguments": args})
    while True:
        line = p.stdout.readline()
        if not line.strip():
            return "(no output)"
        d = json.loads(line)
        if d.get("id") == i:
            res = d.get("result", {})
            txt = "\n".join(c.get("text","") for c in (res.get("content") or []) if isinstance(c, dict))
            return txt or json.dumps(res, ensure_ascii=False)[:1500]
try:
    send(0,"initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}})
    p.stdout.readline()
    print("=== guided_workflows ===")
    print(call("guided_workflows", {}, 10)[:2500])
except Exception as e:
    print("FAILED:", type(e).__name__, e)
finally:
    try: p.kill()
    except Exception: pass
