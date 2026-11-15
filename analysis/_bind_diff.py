import io, json, os, re, glob, collections
R = r'D:\projects\cyber-reverse\replica\src'
bind = json.load(io.open('xaml_bindings.json', encoding='utf-8'))

# index the replica: simple class name -> source text
files = glob.glob(os.path.join(R, '**', '*.cs'), recursive=True)
classes = {}
for f in files:
    try:
        t = io.open(f, encoding='utf-8').read()
    except Exception:
        continue
    for m in re.finditer(r'\bclass\s+([A-Za-z0-9_]+)', t):
        classes.setdefault(m.group(1), []).append((f, t))

renamed = {}
rows = []
for typ, members in sorted(bind.items()):
    simple = typ.split('.')[-1]
    hits = classes.get(simple) or []
    if not hits:
        rows.append((typ, len(members), None, members))
        continue
    text = '\n'.join(t for _, t in hits)
    missing = [m for m in members if not re.search(r'\b' + re.escape(m) + r'\b', text)]
    rows.append((typ, len(members), len(missing), missing))

found = [r for r in rows if r[2] is not None]
nofile = [r for r in rows if r[2] is None]
print('types with a replica class :', len(found))
print('types with NO replica class:', len(nofile))
print('total bound members in found types:', sum(r[1] for r in found))
print('members missing in replica      :', sum(r[2] for r in found))
print()
print('== 缺得最多的 12 个类型 ==')
for typ, n, miss, missing in sorted(found, key=lambda r: -r[2])[:12]:
    print('  %-58s %3d/%-3d 缺: %s' % (typ.split('Cybersole.')[-1], miss, n, ', '.join(missing[:6])))
print()
print('== 没有对应类的类型（前 12） ==')
for typ, n, _, _ in nofile[:12]:
    print('  %-58s %d 个成员' % (typ.split('Cybersole.')[-1], n))
