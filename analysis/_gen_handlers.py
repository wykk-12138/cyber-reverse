import io, re, json
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
h = re.match(r'\s*const HANDLERS = (.*)$', t(158795)).group(1).strip().rstrip(';')
lst = json.loads(h)
print('handlers', len(lst))
print('touch ones', [n for n in lst if 'touch' in n])
print('first 6', lst[:6])
io.open('_handlers.txt','w',encoding='utf-8',newline='').write(h)
