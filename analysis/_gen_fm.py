import io, re, json
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
# FONTS spans several lines: 159071 starts it; collect until a line that ends the object
fonts = t(159071)
m = re.match(r'\s*const FONTS = (.*)$', fonts)
body = m.group(1).strip()
n = 159072
while not body.rstrip().endswith('};') and not body.rstrip().endswith('}') and n < 159260:
    body += t(n).strip()
    n += 1
body = body.rstrip().rstrip(';')
print('fonts chars', len(body), 'ends', body[-50:])
try:
    fo = json.loads(body); print('fonts entries', len(fo)); print(' first key', list(fo)[0], '->', fo[list(fo)[0]])
except Exception as e:
    print('fonts not json:', e)
media = re.match(r'\s*const MEDIA = (.*)$', t(159556)).group(1).strip().rstrip(';')
mo = json.loads(media); print('media entries', len(mo)); print(' sample', list(mo.items())[0])
io.open('_fonts_body.txt','w',encoding='utf-8',newline='').write(body)
io.open('_media_body.txt','w',encoding='utf-8',newline='').write(media)
