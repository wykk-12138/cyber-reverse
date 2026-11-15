import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=300):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=300):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return "ERR "+json.dumps(res["error"],ensure_ascii=False)[:300]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})
for pat in (r'^Getter$', r'^Setter$', r'^Property$'):
    r = call("find_regex", {"pattern": pat, "limit": 5})
    print(pat, '->', r[:200].replace('\n',' '))
