import io, re, json
resume = io.open('docs/RESUME.md', encoding='utf-8').read()
backlog = io.open('docs/BINDING_BACKLOG.md', encoding='utf-8').read()
ratchet = re.search(r'MaxRealGap = (\d+)', io.open('tests/Cybersole.Tests/BindingGapRatchetTests.cs', encoding='utf-8').read()).group(1)
A = json.load(io.open('docs/flow_step_sequences.json', encoding='utf-8'))
wide = json.load(io.open('docs/row_groups_wide.json', encoding='utf-8'))

checks = [
    ('RESUME states the ratchet value', ratchet in resume),
    ('ratchet is a number', ratchet.isdigit()),
    ('backlog title matches ratchet', ('当前 ' + ratchet + ' =') in backlog),
    ('RESUME states a suite count', bool(re.search(r'1[0-9]{3} 通过', resume))),
    ('RESUME says 24 mutations', '24' in resume),
    ('A layout 69', len(A) == 69),
    ('wide B 129', len(wide) == 129),
]
bad = [l for l, ok in checks if not ok]
for label, ok in checks:
    print(('[OK]  ' if ok else '[BAD] ') + label)
print()
print('RESUME numbers >=100:', sorted(set(re.findall(r'\b\d{3,}\b', resume))))
print('mismatches:', bad or 'none')
