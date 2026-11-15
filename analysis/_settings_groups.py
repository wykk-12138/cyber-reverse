import io, re, glob
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
p = re.compile(r'^\s*(0x[0-9a-f]+)\s+(.*)$')
rows = [m.group(2).strip() for m in (p.match(l) for l in lines) if m]
keys = {r for r in rows if re.match(r'^Settings\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)+$', r)}

src = ''
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\**\*.cs', recursive=True):
    src += io.open(f, encoding='utf-8', errors='replace').read()
for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Settings\*.cs'):
    src += io.open(f, encoding='utf-8', errors='replace').read()

groups = {}
for k in keys:
    parts = k.split('.')
    groups.setdefault(parts[1], set()).add(parts[2])
print('%-18s %5s %5s  缺失示例' % ('group', 'keys', '命中'))
for g in sorted(groups):
    leaves = groups[g]
    hit = [l for l in leaves if re.search(r'\b' + re.escape(l) + r'\b', src)]
    miss = sorted(l for l in leaves if l not in hit)
    print('%-18s %5d %5d  %s' % (g, len(leaves), len(hit), ', '.join(miss[:4])))
