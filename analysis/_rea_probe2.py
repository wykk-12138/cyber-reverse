import json, subprocess, time

cmd = ["cmd", "/c", "npx -y rea-agents@6.9.0 mcp"]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     text=True, encoding="utf-8", errors="replace", cwd=r"D:\projects\rea", bufsize=1)
def send(i, m, params=None):
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": m, "params": params or {}}) + "\n")
    p.stdin.flush()
try:
    send(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "probe", "version": "1"}})
    line = p.stdout.readline()
    print("initialize:", (line or "").strip()[:300])
    send(2, "tools/list")
    d = json.loads(p.stdout.readline())
    tools = [t["name"] for t in d.get("result", {}).get("tools", [])]
    print("tools:", len(tools))
    print(", ".join(tools))
except Exception as e:
    print("FAILED:", type(e).__name__, e)
finally:
    try: p.kill()
    except Exception: pass
    err = (p.stderr.read() or "")[:800]
    if err.strip(): print("--- stderr ---\n", err)
