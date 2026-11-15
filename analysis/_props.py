import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
props = t(159605)
m = re.match(r'\s*const CSS_PROPS = (\[.*\])\s*;?\s*$', props)
names = re.findall(r'"([^"]*)"', m.group(1)) if m else []
print('CSS_PROPS line chars', len(props), 'names', len(names))
print('first', names[:5], 'last', names[-3:])
vocab = t(158516)
mv = re.match(r'\s*const CSS_VOCAB = new Set\((.*)\)\s*;?\s*$', vocab)
vn = re.findall(r'"([^"]*)"', mv.group(1)) if mv else []
print('CSS_VOCAB line chars', len(vocab), 'names', len(vn))
print('same list?', names[1:] == [n for n in vn if n != 'constructor'][:len(names)-1] if names and vn else 'n/a')
io.open('_css_props.txt','w',encoding='utf-8',newline='').write(m.group(1) if m else '')
