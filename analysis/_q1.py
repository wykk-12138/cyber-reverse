import json, urllib.request
URL='http://127.0.0.1:13337/mcp'; _id=[0]
def rpc(m,p=None,t=180):
    _id[0]+=1
    b=json.dumps({'jsonrpc':'2.0','id':_id[0],'method':m,'params':p or {}}).encode()
    r=urllib.request.Request(URL,data=b,headers={'Content-Type':'application/json','Accept':'application/json'})
    with urllib.request.urlopen(r,timeout=t) as x: return json.loads(x.read().decode('utf-8','replace'))
def call(tool,args,t=180):
    res=rpc('tools/call',{'name':tool,'arguments':args},t)
    if 'error' in res: return 'ERR '+json.dumps(res['error'],ensure_ascii=False)
    out=res.get('result',{})
    return '\n'.join(c.get('text','') for c in (out.get('content') or []) if isinstance(c,dict)) or json.dumps(out,ensure_ascii=False)

rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'x','version':'1'}})
print('--- names containing MonitorView ---')
print(call('entity_query',{'queries':[{'kind':'names','regex':'MonitorView','count':20}]})[:900])
print('--- functions named *.ctor-ish with Toggle ---')
print(call('func_query',{'queries':[{'name_regex':'Toggle','count':20}]})[:900])
