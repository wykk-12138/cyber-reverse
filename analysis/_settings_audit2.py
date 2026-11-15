import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs', encoding='utf-8').read()
m = re.search(r'public (?:sealed )?class GlobalSettings[^{]*\{', src)
start = m.end()
depth, i = 1, start
while i < len(src) and depth:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]
props = re.findall(r'^\s{4}public\s+[A-Za-z0-9_<>\?\[\],\s\.]+?\s(\w+)\s*\{\s*get', body, re.M)
print('GlobalSettings properties:', len(props))
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m2.group(2).strip() for m2 in (p.match(l) for l in lines) if m2}
lower = {x.lower() for x in pool}
hit = [x for x in props if x in pool or x.lower() in lower]
miss = [x for x in props if x not in pool and x.lower() not in lower]
print('in pool: %d   not: %d' % (len(hit), len(miss)))
print('not in pool:', ', '.join(miss))
