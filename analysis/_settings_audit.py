import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs', encoding='utf-8').read()
props = re.findall(r'public\s+[\w<>\[\]\?,\s]+\s+(\w+)\s*\{\s*get', src)
print('replica GlobalSettings properties:', len(props))

lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
pool = {m.group(2).strip() for m in (p.match(l) for l in lines) if m}
lower = {x.lower() for x in pool}
hit = [x for x in props if x in pool or x.lower() in lower]
miss = [x for x in props if x not in pool and x.lower() not in lower]
print('in pool: %d   not: %d' % (len(hit), len(miss)))
print()
print('not in pool:', ', '.join(miss[:30]))
