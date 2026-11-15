import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        "AdvancedView", "ExpressionView", "ProfileCreatorView", "ProfileView",'''
new = '''        //
        // R208 also removed ProfileCreatorView: the same page's "Add Profile" button hosts it, so the baseline shrank
        // again (36 -> 35).
        "AdvancedView", "ExpressionView", "ProfileView",'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('removed ProfileCreatorView')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '| UI 类 | 92 个，**36 个不可达**（39%） | `UnreachedUiTypesTests` |'
new2 = '| UI 类 | 92 个，**35 个不可达**（38%） | `UnreachedUiTypesTests` |'
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2))
print('guide counts updated again')
