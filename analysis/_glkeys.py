import io, json, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = json.loads(re.match(r'\s*const GL_PARAMS = (.*)$', src[159016][12:]).group(1).strip().rstrip(';'))
w = p['webgl']
for k in ('7936','7937','37445','37446','7938','35724'):
    print(k, '->', repr(w.get(k)))
