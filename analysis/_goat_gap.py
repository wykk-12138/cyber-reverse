import io, re, collections
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
goat = sorted({r for r in rows if 'goat.com/web-api' in r or 'web-api/v1' in r and 'goat' in r})
print('GOAT evidenced web-api paths:', len(goat))
for g in goat: print('   ', g[:120])
print()
# what the replica actually calls on Goat
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs', encoding='utf-8').read()
used = sorted(set(re.findall(r'WebApi\(c, \$?"(/[^"$]+)"', src)))
print('replica uses:', used)
print()
print('池里有、复刻件没用的:')
for g in goat:
    path = re.sub(r'^https://www\.goat\.com', '', g).split('?')[0]
    if not any(path.startswith(u) or u in path for u in used):
        print('   ', path[:80])
