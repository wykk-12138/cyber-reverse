import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=900):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=900):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return "ERR "+json.dumps(res["error"],ensure_ascii=False)[:400]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})
# 描述符 0x14320c54d 的 RVA = 0x320c54d；LE 字节 4D C5 20 03
# 也搜「指向它的 VA」(0x14320c54d -> 4D C5 20 43 01 00 00 00)
print("== RVA 4DC52003 ==")
print(call("find_bytes", {"patterns": ["4D C5 20 03"], "limit": 20})[:700])
print("== VA 4DC5204301000000 ==")
print(call("find_bytes", {"patterns": ["4D C5 20 43 01 00 00 00"], "limit": 20})[:700])
