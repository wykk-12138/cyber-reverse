import json, urllib.request
URL = 'http://127.0.0.1:13337/mcp'; _id=[0]
def rpc(m, p=None):
    _id[0]+=1
    body=json.dumps({'jsonrpc':'2.0','id':_id[0],'method':m,'params':p or {}}).encode()
    req=urllib.request.Request(URL,data=body,headers={'Content-Type':'application/json','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode('utf-8','replace'))
rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'x','version':'1'}})
tools={t['name']:t for t in rpc('tools/list',{})['result']['tools']}
for n in ('func_query','decompile','xrefs_to','find_regex','search_text','disasm','list_funcs'):
    t=tools.get(n)
    if not t: print(n,'MISSING'); continue
    props=t['inputSchema'].get('properties',{})
    req=t['inputSchema'].get('required',[])
    print('%-12s req=%s  params=%s' % (n, req, ', '.join('%s:%s'%(k,v.get('type','?')) for k,v in props.items())[:220]))
    print('    desc:', (t.get('description') or '')[:120].replace('\n',' '))
