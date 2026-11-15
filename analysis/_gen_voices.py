import io, re, json
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
def t(n): return src[n-1][12:]
body = re.match(r'\s*const VOICES = (.*)$', t(160110)).group(1).strip()
n = 160111
# the literal continues across lines; balance brackets
depth = body.count('[') - body.count(']') + body.count('{') - body.count('}')
while depth > 0 and n < 160140:
    body += t(n).strip()
    depth = body.count('[') - body.count(']') + body.count('{') - body.count('}')
    n += 1
body = body.rstrip().rstrip(';')
print('chars', len(body), 'ends', body[-40:], 'lines to', n-1)
v = json.loads(body)
print('voices', len(v))
for row in v[:3]: print('  ', row.get('name'), '|', row.get('voiceURI'), '|', row.get('lang'), '|', row.get('localService'), row.get('default'))
io.open('_voices.txt','w',encoding='utf-8',newline='').write(body)
