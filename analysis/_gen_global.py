import io, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
kinds_line = t(160017)
m = re.match(r'\s*const GLOBAL_KINDS = (.*)$', kinds_line)
kinds = m.group(1).rstrip()
if not kinds.endswith('}'):
    print('WARN kinds may continue')
nf_line = t(160018)
m2 = re.match(r'\s*const GLOBAL_NOT_FN = new Set\((.*)\)\s*;?\s*$', nf_line)
nf = m2.group(1) if m2 else None
print('kinds chars', len(kinds), 'ends', kinds[-30:])
print('notfn chars', len(nf) if nf else None, 'ends', (nf or '')[-30:])
import json
try:
    obj = json.loads(kinds)
    print('kinds entries', len(obj), 'sample', list(obj.items())[:3])
except Exception as e:
    print('kinds not pure JSON:', e)
try:
    lst = json.loads(nf)
    print('notfn entries', len(lst), 'sample', lst[:6])
except Exception as e:
    print('notfn not pure JSON:', e)
io.open('_kinds.txt','w',encoding='utf-8',newline='').write(kinds)
io.open('_notfn.txt','w',encoding='utf-8',newline='').write(nf or '')
