import io, re
R = r'D:\projects\cyber-reverse\replica'

# 1) EmptyView is now built -> leaves NotBuiltYet (5 -> 4), same 70 -> 71
p = R + r'\tests\Cybersole.Tests\OriginalViewClassParityTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        "EmptyView",                // the empty state is a UiKit helper, not a view class''',
'''        // R209: EmptyView is built. Every page's empty state came from a hand-built block in that page; there is now
        // one control (Views/Common/EmptyView.cs) that owns the glyph, the headline and the per-page second line.''')
t = t.replace('''        Assert.Equal(70, same);          // R204: ProxyCreatorView left the debt''',
'''        Assert.Equal(71, same);          // R209: EmptyView left the debt''')
t = t.replace('''        Assert.Equal(5, notBuilt);''',
'''        Assert.Equal(4, notBuilt);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('parity buckets updated')

# 2) guide counts: 92 UI classes -> 93 (EmptyView added); unreachable stays 36
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 92 个，**36 个不可达**（39%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 93 个，**36 个不可达**（39%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide total updated')

# 3) parity doc: 78 -> 79 UI classes (24 Window + 55 UserControl)
p3 = R + r'\docs\PARITY.md'
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace('**78 个 UI 类：24 个 `Window` 子类 + 54 个 `UserControl` 子类。**',
                '**79 个 UI 类：24 个 `Window` 子类 + 55 个 `UserControl` 子类。**')
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('parity doc updated')
