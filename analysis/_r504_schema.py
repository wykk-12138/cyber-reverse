import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; n=[0]
def rpc(m,p=None,t=600):
    n[0]+=1
    b=json.dumps({"jsonrpc":"2.0","id":n[0],"method":m,"params":p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Content-Type":"application/json","Accept":"application/json"})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode("utf-8","replace"))
rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"x","version":"1"}})
tools={t["name"]:t for t in rpc("tools/list",{})["result"]["tools"]}
for nm in ("find_bytes","search_bytes","get_bytes","read_bytes","entity_query"):
    if nm in tools:
        sch=tools[nm].get("inputSchema",{})
        print(nm, "req=", sch.get("required"), "| props=", list((sch.get("properties") or {}).keys())[:8])
