import json, urllib.request, re
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=600):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
def call(tool,args,t=600):
    res=rpc("tools/call",{"name":tool,"arguments":args},t)
    if "error" in res: return "ERR "+json.dumps(res["error"],ensure_ascii=False)[:300]
    out=res.get("result",{})
    return "\n".join(c.get("text","") for c in (out.get("content") or []) if isinstance(c,dict)) or "{}"
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})

raw = call("get_string", {"addrs": ["0x143211210"]})
val = json.loads(raw)[0]["value"]
print("blob chars:", len(val))
# 验证「[长度字节][文本]」假设
i = 0; ok = 0; bad = 0; samples = []
while i < len(val):
    L = ord(val[i]); i += 1
    if L < 8 or i + L > len(val):
        bad += 1; break
    s = val[i:i+L]; i += L
    if s.endswith('!Getter') or s.endswith('!Setter'):
        ok += 1
        if len(samples) < 6: samples.append(s)
    else:
        bad += 1; break
print("parsed descriptors:", ok, "| broke at:", bad)
for s in samples: print("   ", s)
