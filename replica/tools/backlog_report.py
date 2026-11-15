"""按"类型在复刻件里存不存在"给绑定缺口分类。

用法（仓库根目录）：
    <python> tools\backlog_report.py

A 类 = 类已存在、只差成员（可以一轮做掉几个）
B 类 = 类不存在（要先抽控件/扩模型，或记为结构差异）
数字口径与 tests/Cybersole.Tests/BindingGapRatchetTests.cs 一致：剥注释 + 排除泛型噪音。
"""

import io, json, re, glob
BIND = r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json'
bind = json.load(io.open(BIND, encoding='utf-8'))
NOISE = re.compile(r'^(HasMultiple|Value)_\d+$')

def strip(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'(?<!:)//[^\n]*', ' ', s)

files = glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True)
blob = '\n'.join(strip(io.open(f, encoding='utf-8').read()) for f in files)
classes = set(re.findall(r'\bclass\s+([A-Za-z0-9_]+)', blob))

rows = []
for typ, members in bind.items():
    simple = typ.split('.')[-1].split('`')[0]
    miss = [m for m in members if not re.search(r'\b'+re.escape(m)+r'\b', blob) and not NOISE.match(m)]
    if miss:
        rows.append((simple, simple in classes, miss, typ))

existing = [r for r in rows if r[1]]
other = [r for r in rows if not r[1]]
print('classes that EXIST in the replica but miss members:', len(existing), '->', sum(len(r[2]) for r in existing), 'members')
for simple, _, miss, typ in sorted(existing, key=lambda r: -len(r[2])):
    print('  %-32s %s' % (simple, ', '.join(miss)))
print()
print('types that DO NOT exist (structural):', len(other), '->', sum(len(r[2]) for r in other), 'members')
for simple, _, miss, typ in sorted(other, key=lambda r: -len(r[2])):
    print('  %-32s %s' % (simple, ', '.join(miss)))
