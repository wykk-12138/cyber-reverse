import io, re, glob, json
checks = {
  '18 条': ['docs/FLOW_SEQUENCES.md', 'docs/SESSION_STATE.md'],
  '69 段': ['docs/FLOW_SEQUENCES.md', 'docs/SESSION_STATE.md'],
  '141 步': ['docs/FLOW_SEQUENCES.md', 'docs/SESSION_STATE.md'],
  'MaxRealGap': ['tests/Cybersole.Tests/BindingGapRatchetTests.cs'],
}
for needle, files in checks.items():
    for f in files:
        t = io.open(f, encoding='utf-8').read()
        n = t.count(needle)
        print('%-12s %-34s %d 次' % (needle, f, n))
print()
# the numbers that must agree
doc = io.open('docs/BINDING_BACKLOG.md', encoding='utf-8').read()
ratchet = re.search(r'MaxRealGap = (\d+)', io.open('tests/Cybersole.Tests/BindingGapRatchetTests.cs', encoding='utf-8').read()).group(1)
head = re.search(r'当前 (\d+) =', doc)
print('账本标题:', head.group(1) if head else '未找到', ' 棘轮:', ratchet, ' 一致' if head and head.group(1) == ratchet else ' ★不一致')
# artifact numbers vs doc claims
segs = json.load(io.open('docs/flow_step_sequences.json', encoding='utf-8'))
wide = json.load(io.open('docs/row_groups_wide.json', encoding='utf-8'))
cons = json.load(io.open('docs/row_groups.json', encoding='utf-8'))
print('实际: A 布局 %d 段, B 保守 %d 段, B 宽 %d 段' % (len(segs), len(cons), len(wide)))
