import io, json, os, re, glob, sys

# 从原版的 XAML 绑定表（docs/xaml_bindings.json）反查复刻件：
#   用法: python bind_diff.py [--per-file] [--buckets] [--type-presence]
#   默认在整个 src/ 里找成员名（"行为是否存在"）；--per-file 只在同名类所在文件里找（"这个类是否暴露它"）。
#
#   --type-presence（R434，为什么现有不够用）：
#       bind_scope.py 只查"成员是否在同一个类型 body 内"，bind_diff.py 只查"成员名是否在源码某处出现"。
#       两者都发现不了**类型整体不存在**：`Cybersole.Models.Input` 在复刻件里根本没有这个类，
#       但它的唯一成员 `Type` 在源码里满地都是（`Input.Type` 的字符串、别的类的 Type 属性），
#       于是两个工具都判它"没问题"。R434 实测确认这是第三类缺口（类型缺失），与"名字级 16 / 类型级 4"不同。
#       本开关对绑定表里 174 个类型逐个检查源码是否存在同名类型声明。
R = r'D:\projects\cyber-reverse\replica\src'
BIND = r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json'

per_file = '--per-file' in sys.argv
bind = json.load(io.open(BIND, encoding='utf-8'))

files = glob.glob(os.path.join(R, '**', '*.cs'), recursive=True)
texts = []
for f in files:
    try:
        texts.append((f, io.open(f, encoding='utf-8').read()))
    except Exception:
        pass
def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'(?<!:)//[^\n]*', ' ', s)

blob = '\n'.join(strip_comments(t) for _, t in texts)

by_class = {}
for f, t in texts:
    for m in re.finditer(r'\bclass\s+([A-Za-z0-9_]+)', t):
        by_class.setdefault(m.group(1), []).append(t)

rows, missing_total = [], 0
for typ, members in sorted(bind.items()):
    if per_file:
        simple = typ.split('.')[-1]
        scope = '\n'.join(by_class.get(simple, []))
        if not scope:
            rows.append((typ, len(members), None, members))
            continue
    else:
        scope = blob

    missing = [m for m in members if not re.search(r'\b' + re.escape(m) + r'\b', scope)]
    missing_total += len(missing)
    rows.append((typ, len(members), len(missing), missing))

scope_label = 'per-file' if per_file else 'whole-source'

# R1184: the classification that turns "15 types absent" into a number with a meaning. Renaming is allowed
# (AGENTS.md §0), and R702 placed two of these outside the function set, so the table lives beside the tool and
# every absent type must appear in it; anything missing shows up as "unclassified" rather than quietly counting
# as a gap.
CLASSIFICATION = {}
_classification_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'type_classification.json')
if os.path.exists(_classification_path):
    CLASSIFICATION = json.load(io.open(_classification_path, encoding='utf-8')).get('types', {})

if '--type-presence' in sys.argv:
    declared = set()
    for m in re.finditer(r'\b(?:class|record|struct|enum|interface)\s+([A-Za-z0-9_]+)', blob):
        declared.add(m.group(1))
    present, absent = [], []
    for typ, members in sorted(bind.items()):
        simple = typ.split('.')[-1].split('`')[0]
        (present if simple in declared else absent).append((typ, members))
    print('type presence: %d declared in bindings, %d present in source, %d absent'
          % (len(bind), len(present), len(absent)))
    for typ, members in absent:
        entry = CLASSIFICATION.get(typ)
        if entry:
            kind = entry.get('kind', '?')
            to = entry.get('to')
            print('  ABSENT  %-42s %-12s %s' % (typ, kind, to or ''))
        else:
            print('  ABSENT  %-42s (members: %s)' % (typ, ', '.join(sorted(members))))
    if absent:
        renamed = sum(1 for typ, _ in absent if CLASSIFICATION.get(typ, {}).get('kind') == 'renamed')
        not_in_function_set = sum(1 for typ, _ in absent if CLASSIFICATION.get(typ, {}).get('kind') == 'not_in_function_set')
        unimplemented = sum(1 for typ, _ in absent if CLASSIFICATION.get(typ, {}).get('kind') == 'unimplemented')
        unclassified = len(absent) - renamed - not_in_function_set - unimplemented
        print()
        print('classified: renamed %d, not in function set %d, unimplemented %d, unclassified %d'
              % (renamed, not_in_function_set, unimplemented, unclassified))
        print()
        print('note: ABSENT = no same-name declaration anywhere in src/. The replica is allowed to rename')
        print('      types (AGENTS.md §0), so each ABSENT must be classified in tools/type_classification.json')
        print('      as RENAMED (with the counterpart), NOT_IN_FUNCTION_SET (with the ruling) or UNIMPLEMENTED.')
    sys.exit(0)

print(f'scope: {scope_label}   types: {len(bind)}   members: {sum(len(v) for v in bind.values())}')
print(f'missing: {missing_total}')
print()
NOISE = re.compile(r'^(HasMultiple|Value)_\d+$')      # generic instantiation artefacts, not design members
# R1174: two members that are a decision, not a gap. R702 classified the login-credential and licence UI as
# not part of the replica's function set (docs/DECISION_LICENSE_OUT_OF_SCOPE.md), and these are exactly its two
# bound members. Counting them under "real gap" made the metric read like outstanding work; a test pins both the
# zero and the exact size of this set, so it cannot quietly grow.
NOT_IN_FUNCTION_SET = {
    ('Ui.Views.Auth.AuthWindow', 'Logout'),
    ('Ui.Views.Auth.LicenseControl', 'Authenticate'),
}
if '--buckets' in sys.argv:
    noise = sum(1 for r in rows if r[2] for m in r[3] if NOISE.match(m))
    excluded = sum(1 for r in rows for m in r[3]
                   if not NOISE.match(m) and (r[0].split('Cybersole.')[-1], m) in NOT_IN_FUNCTION_SET)
    real = missing_total - noise - excluded
    print(f'noise (HasMultiple_NN): {noise}')
    print(f'not in function set   : {excluded}')
    print(f'real gap              : {real}')
    print()
    for typ, n, miss, missing in sorted([r for r in rows if r[2]], key=lambda r: -r[2]):
        short = typ.split('Cybersole.')[-1]
        real_missing = [m for m in missing
                        if not NOISE.match(m) and (short, m) not in NOT_IN_FUNCTION_SET]
        if real_missing:
            print('  %-50s %2d  %s' % (short, len(real_missing), ', '.join(real_missing[:8])))
    sys.exit(0)

for typ, n, miss, missing in sorted([r for r in rows if r[2]], key=lambda r: -r[2])[:20]:
    print('  %-50s %3d/%-3d  %s' % (typ.split('Cybersole.')[-1], miss, n, ', '.join(missing[:8])))
