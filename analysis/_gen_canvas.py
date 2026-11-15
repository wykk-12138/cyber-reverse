import io, re, json
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
canvas = t(159269)
m = re.match(r'\s*const CANVAS = (.*)$', canvas)
body = m.group(1).strip()
if body.endswith(';'): body = body[:-1]
print('canvas chars', len(body), 'ends', body[-40:])
try:
    obj = json.loads(body)
    print('canvas entries', len(obj))
    for k, v in obj.items():
        print('  ', k, '->', v[:60], '... len', len(v))
except Exception as e:
    print('not json:', e)
prog = []
for n in range(159319, 159330):
    txt = t(n).strip()
    if txt.startswith('"96x48'): prog.append(txt)
print('program lines', len(prog))
for p in prog:
    print('  ', p[:90], '... len', len(p))
io.open('_canvas_table.txt','w',encoding='utf-8',newline='').write(body)
io.open('_programs.txt','w',encoding='utf-8',newline='').write('\n'.join(prog))
