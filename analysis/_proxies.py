import io, re
lines = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
for ln in lines:
    m = pat.match(ln)
    if not m: continue
    t = m.group(2)
    if t in ('SOCKS5','SOCKS4','HTTP','HTTPS','socks5','socks4','http') or t.startswith('Proxy'):
        print(m.group(1), repr(t))
