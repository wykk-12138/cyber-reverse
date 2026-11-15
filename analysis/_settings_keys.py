import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
keys = sorted({r for r in rows if re.match(r'^Settings\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)+$', r)})
print('Settings.* locale keys in the pool:', len(keys))
groups = {}
for k in keys:
    parts = k.split('.')
    groups.setdefault(parts[1], set()).add(parts[2])
for g in sorted(groups):
    print('  %-14s %d 个 key' % (g, len(groups[g])))
print()
leaves = sorted({k.split('.')[2] for k in keys})
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\GlobalSettings.cs', encoding='utf-8').read()
m = re.search(r'public (?:sealed )?class GlobalSettings[^{]*\{', src)
start = m.end(); depth, i = 1, start
while i < len(src) and depth:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]
props = set(re.findall(r'^\s{4}public\s+[A-Za-z0-9_<>\?\[\],\s\.]+?\s(\w+)\s*\{\s*get', body, re.M))
missing = [l for l in leaves if l not in props]
print('Settings 叶子名在池子里、但复刻件 GlobalSettings 没有:', len(missing))
print(', '.join(missing[:24]))
