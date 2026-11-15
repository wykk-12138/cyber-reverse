import io, json, os, re, glob
BIND = r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json'
bind = json.load(io.open(BIND, encoding='utf-8'))
NOISE = re.compile(r'^(HasMultiple|Value)_\d+$')
files = [f for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True)]
blob = '\n'.join(io.open(f, encoding='utf-8').read() for f in files)
classes = set(re.findall(r'\bclass\s+([A-Za-z0-9_]+)', blob))
rows = []
for typ, members in bind.items():
    simple = typ.split('.')[-1].split('`')[0]
    miss = [m for m in members if not re.search(r'\b'+re.escape(m)+r'\b', blob) and not NOISE.match(m)]
    if miss:
        rows.append((simple, simple in classes, miss))
print('%-34s %-8s %s' % ('type', 'exists', 'missing'))
for simple, exists, miss in sorted(rows, key=lambda r: (not r[1], -len(r[2]))):
    print('%-34s %-8s %s' % (simple, 'YES' if exists else 'no', ', '.join(miss)))
