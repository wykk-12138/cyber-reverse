import json, urllib.request
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
val = json.loads(call("get_string", {"addrs": ["0x143211210"]}))[0]["value"]
# 打印分隔符的位置与字节值，看真实编码
import re
for m in re.finditer(r'[^A-Za-z0-9_.`!,\u0080-\uffff]', val):
    pass
parts = re.split(r'(!Getter|!Setter)', val)
print("repr 前 300 字符:")
print(repr(val[:300]))
