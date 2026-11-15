import json, os, subprocess
node = r"D:\tools\node24\node-v24.22.1-win-x64\node.exe"
script = r"D:\tools\rea-agents\node_modules\rea-agents\scripts\rea.mjs"
env = {**os.environ, "PATH": os.path.dirname(node) + os.pathsep + os.environ["PATH"]}
p = subprocess.Popen([node, script, "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                     cwd=r"D:\tools\rea-agents", bufsize=1, env=env)
n=[0]
def send(m, params=None):
    n[0]+=1
    p.stdin.write(json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":params or {}})+"\n"); p.stdin.flush(); return n[0]
def call(tool,args):
    i=send("tools/call",{"name":tool,"arguments":args})
    while True:
        line=p.stdout.readline()
        if not line.strip(): return "(none)"
        d=json.loads(line)
        if d.get("id")==i:
            res=d.get("result",{})
            return "\n".join(c.get("text","") for c in (res.get("content") or []) if isinstance(c,dict)) or json.dumps(res,ensure_ascii=False)[:2000]
try:
    send("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}); p.stdout.readline()
    for wf in ("verify_reconstruction","investigate_feature"):
        out = call("guided_workflows", {"action":"render","workflow_id":wf})
        open(rf"D:\projects\cyber-reverse\analysis\rea-workflow-{wf}.json","w",encoding="utf-8").write(out)
        print("===", wf, "chars:", len(out))
        print(out[:1400].replace("\\n","\n"))
except Exception as e:
    print("FAILED:", type(e).__name__, e)
finally:
    try: p.kill()
    except Exception: pass
