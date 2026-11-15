import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; _id=[0]
def rpc(m,p=None):
    _id[0]+=1
    b=json.dumps({'jsonrpc':'2.0','id':_id[0],'method':m,'params':p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={'Content-Type':'application/json','Accept':'application/json'})
    with urllib.request.urlopen(r,timeout=60) as x: return json.loads(x.read().decode('utf-8','replace'))
rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'x','version':'1'}})
tools={t['name']:t for t in rpc('tools/list',{})['result']['tools']}
for n in ('func_query','entity_query','find'):
    print('===', n)
    print(json.dumps(tools[n]['inputSchema'], ensure_ascii=False)[:1200])
