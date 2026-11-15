import io, re
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def text_at(n):
    return src[n-1][12:]
css = text_at(158512)
print('css decl line len', len(css))
m = re.match(r"\s*const CSS_DECL = \[(.*)\];?\s*$", css)
print('matched', bool(m))
names = re.findall(r'"([^"]*)"', m.group(1)) if m else []
print('css names', len(names), names[:6], names[-3:])
io.open('_css_decl.txt','w',encoding='utf-8',newline='').write(m.group(1).strip() if m else '')
