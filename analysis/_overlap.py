import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
props = re.findall(r'"([^"]*)"', re.match(r'\s*const CSS_PROPS = (\[.*\])\s*;?\s*$', t(159605)).group(1))
decl  = re.findall(r'"([^"]*)"', re.match(r'\s*const CSS_DECL = (\[.*\])\s*;?\s*$', t(158512)).group(1))
print('CSS_PROPS', len(props), 'CSS_DECL', len(decl))
overlap = [n for n in decl if n in props]
print('CSS_DECL names that also appear in CSS_PROPS:', overlap)
for probe in ('length','cssText','parentRule','item','getPropertyValue','setProperty','cssFloat','removeProperty','cssRules','getPropertyCSSValue','constructor'):
    print(f'  {probe:22} in CSS_PROPS: {probe in props}')
