import io, re
R = r'D:\projects\cyber-reverse\replica'

# (c) drop ProfileCsvEditorView from the unreachable baseline (now constructed by BillingView)
p = R + r'\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        // Profiles
        "AdvancedView", "ExpressionView", "ProfileCreatorView", "ProfileView",'''
new = '''        // Profiles
        //
        // R208 removed ProfileCsvEditorView: the Billing page's measured "CSV Editor" button now hosts it through
        // ViewHostModal, so it is constructed and the baseline shrank by one (37 -> 36).
        "AdvancedView", "ExpressionView", "ProfileCreatorView", "ProfileView",'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('baseline updated')

# (d) VERDICT guide counts 92 / 37 -> 92 / 36
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '| UI 类 | 92 个，**37 个不可达**（40%） | `UnreachedUiTypesTests` |'
new2 = '| UI 类 | 92 个，**36 个不可达**（39%） | `UnreachedUiTypesTests` |'
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2))
print('guide counts updated')
