import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=900):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=900):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return json.dumps({"ERR":res["error"]},ensure_ascii=False)[:300]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})
r = call("entity_query", {"queries":[{"kind":"strings","min_addr":"0x143200000","max_addr":"0x1432a0000","count":12,"fields":["addr","length","text"]}]})
try:
    rows = json.loads(r)[0]["data"]
except Exception as e:
    print("parse fail:", r[:300]); rows=[]
print("sampled strings:", len(rows))
addrs = [x["addr"] for x in rows]
if addrs:
    xr = call("xrefs_to", {"addrs": addrs, "limit": 5})
    print(xr[:1200])
