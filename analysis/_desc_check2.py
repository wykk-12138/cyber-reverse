import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=300):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=300):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return "ERR "+json.dumps(res["error"],ensure_ascii=False)[:400]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})
# 看 MonitorView 那批地址附近是什么形态
for a in ("0x1432111cd","0x143211210","0x14321141a","0x14363b623"):
    print(a, '->', call("get_string", {"addr": a})[:160].replace('\n',' '))
