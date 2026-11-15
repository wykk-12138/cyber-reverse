import io, re, json
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
params = re.match(r'\s*const GL_PARAMS = (.*)$', t(159017)).group(1).strip().rstrip(';')
meta = re.match(r'\s*const GL_META = (.*)$', t(159018)).group(1).strip().rstrip(';')
print('params chars', len(params), 'ends', params[-40:])
print('meta chars', len(meta), 'ends', meta[-40:])
try:
    p = json.loads(params); print('params kinds', list(p.keys()), 'webgl enums', len(p['webgl']), 'webgl2 enums', len(p.get('webgl2', {})))
    print(' sample', list(p['webgl'].items())[:3])
except Exception as e:
    print('params not json:', e)
try:
    m = json.loads(meta); print('meta kinds', list(m.keys()))
    for k, v in m.items(): print('  ', k, 'extensions', len(v.get('extensions', [])), 'attributes', list(v.get('attributes', {}).keys()), 'precisions', list(v.get('precisions', {}).keys())[:3])
except Exception as e:
    print('meta not json:', e)
io.open('_gl_params.txt','w',encoding='utf-8',newline='').write(params)
io.open('_gl_meta.txt','w',encoding='utf-8',newline='').write(meta)
