import json, urllib.request, re
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=600):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=600):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return "ERR "+str(res["error"])[:200]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})

PAT = re.compile(r'([A-Za-z_][\w.`]*\.[A-Za-z_][\w.`]*),([A-Za-z_][\w.`]*\.[A-Za-z_][\w.`]*)!(Getter|Setter)')
total = 0
for addr in ("0x1432111cd","0x143211210","0x14321141a","0x14321189b","0x143211967","0x14363b623"):
    v = json.loads(call("get_string", {"addrs": [addr]}))[0]["value"]
    hits = PAT.findall(v)
    total += len(hits)
    print(addr, "len=%d" % len(v), "descriptors=%d" % len(hits), "| e.g.", hits[0] if hits else None)
print("total descriptors in these 6 blobs:", total)
