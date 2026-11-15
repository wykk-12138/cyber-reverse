import io, re
# 1) baseline gains the new control (declared on purpose, not yet placed on a page — R265 rule)
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '        "ComboBoxEdit"'
if anchor in t:
    print('already in baseline')
else:
    m = re.search(r'(private static readonly string\[\] Baseline\s*=\s*\n\s*\{\n)', t)
    assert m, 'baseline array not found'
    add = '        // R312: a control extracted from the binding table with no proven page yet — declared, tested, unreachable.\n        "ComboBoxEdit",\n'
    t = t[:m.end(1)] + add + t[m.end(1):]
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('baseline updated')

# 2) the guide and PARITY.md UI counts move 97 -> 98, unreachable 29 -> 30
for path, subs in (
  (r'D:\projects\cyber-reverse\replica\docs\VERDICT.md',
   [('| UI 类 | 97 个，**29 个不可达**（30%） | `UnreachedUiTypesTests` |',
     '| UI 类 | 98 个，**30 个不可达**（31%） | `UnreachedUiTypesTests` |')]),
):
    tt = io.open(path, encoding='utf-8').read()
    for old, new in subs:
        if old in tt: tt = tt.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='').write(tt)
    print('guide updated:', path.split('\\')[-1])
