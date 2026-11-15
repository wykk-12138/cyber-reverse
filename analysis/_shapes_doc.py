import io, re, collections, json

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
BINDS = r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json'
OUT = r'D:\projects\cyber-reverse\replica\docs\BINDING_SHAPES.md'

lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]

shape = collections.defaultdict(lambda: collections.defaultdict(set))
for r in rows:
    for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
        member, kind = m.group(1), m.group(2)
        idx = r.find(',Cybersole.' + member + '!' + kind)
        if idx <= 0:
            continue
        head = r[:idx]
        t = re.split(r'[,\s]', head)[-1].split('.')[-1]
        shape[t][member].add(kind)

binds = json.load(io.open(BINDS, encoding='utf-8'))
lines_out = [
    '# 绑定成员的形状（Property / Getter / Setter）',
    '',
    '来源：字符串池里的编译期访问器名（`<Type>,Cybersole.<Member>!Property|Getter|Setter`）。',
    '生成器：`python tools/bind_shape.py [过滤词]`。',
    '',
    '**怎么读**：',
    '',
    '- `Getter,Property,Setter` → 原件里是**可读写属性**（用户动作多半是 `ICommand` 属性）；',
    '- `Getter,Property` → **只读属性**（数据）；',
    '- `-` → 池子里没有该成员的访问器证据（可能是方法，或证据在别处）。',
    '',
    '**用途**：新增成员时先看这里，按原件的形状写（动作写 `ICommand` 属性，数据写只读属性）。',
    '',
]

with_evidence = 0
for full, members in sorted(binds.items()):
    short = full.split('.')[-1]
    ev = shape.get(short)
    if not ev:
        continue
    with_evidence += 1
    lines_out.append('## ' + short)
    lines_out.append('')
    lines_out.append('| 成员 | 形状 |')
    lines_out.append('|---|---|')
    for m in sorted(members):
        kinds = ev.get(m)
        lines_out.append('| `%s` | %s |' % (m, '`' + ','.join(sorted(kinds)) + '`' if kinds else '—'))
    lines_out.append('')

lines_out.insert(6, '**覆盖**：%d 个类型在池子里有访问器证据。\n' % with_evidence)
io.open(OUT, 'w', encoding='utf-8', newline='').write('\n'.join(lines_out))
print('BINDING_SHAPES.md written, types with evidence:', with_evidence)
