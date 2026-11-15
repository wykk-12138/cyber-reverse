import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
seg = t(159605)
m = re.match(r'\s*const CSS_PROPS = (\[.*\])\s*;?\s*$', seg)
names = re.findall(r'"([^"]*)"', m.group(1))
print('CSS_PROPS', len(names), 'chars', len(seg))
# a sample of the camelCase ones, and the dashed conversion rule
sample = [n for n in names if n[:1].islower()][:8]
print('camel sample', sample)
print('count starting with A-Z (dashed form)', sum(1 for n in names if n[:1].isupper()))
print('epub count', sum(1 for n in names if n.startswith('epub')))
print('webkit count', sum(1 for n in names if n.startswith('webkit')))
io.open('_css_props.txt','w',encoding='utf-8',newline='').write(m.group(1))
