import json, subprocess, sys, time, os

msg = lambda i, m, p=None: json.dumps({"jsonrpc":"2.0","id":i,"method":m,"params":p or {}}) + "\n"
p = subprocess.Popen(["npx.cmd","-y","rea-agents@6.9.0","mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", cwd=r"D:\projects\rea")
try:
    p.stdin.write(msg(1,"initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}))
    p.stdin.flush()
    t0 = time.time()
    line = p.stdout.readline()
    print("initialize:", line[:400].strip())
    p.stdin.write(msg(2,"tools/list",{})); p.stdin.flush()
    line = p.stdout.readline()
    d = json.loads(line)
    tools = [t["name"] for t in d.get("result",{}).get("tools",[])]
    print("tools:", len(tools))
    print(", ".join(tools[:60]))
except Exception as e:
    print("FAILED:", type(e).__name__, e)
finally:
    try: p.kill()
    except Exception: pass
    err = p.stderr.read()[:600] if p.stderr else ""
    if err.strip(): print("--- stderr ---\n", err)
