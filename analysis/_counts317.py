import io, re
# baseline gains InputRow (the one row type the design deliberately leaves unplaced)
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
if '"InputRow"' in t:
    print('InputRow already in baseline')
else:
    m = re.search(r'(private static readonly string\[\] Baseline\s*=\s*\n\s*\{\n)', t)
    add = '        // R317: a suggestion-list row from the binding table with no proven page yet — declared and tested only.\n        "InputRow",\n'
    t = t[:m.end(1)] + add + t[m.end(1):]
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('baseline + InputRow')

# guide counts: 99/30 -> 103/31
p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
old = '| UI 类 | 99 个，**30 个不可达**（30%） | `UnreachedUiTypesTests` |'
new = '| UI 类 | 103 个，**31 个不可达**（30%） | `UnreachedUiTypesTests` |'
assert old in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old, new, 1))
print('guide 103 / 31')
