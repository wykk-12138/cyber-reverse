import io
R = r'D:\projects\cyber-reverse\replica'

# GroupGrid is built -> notBuilt 4 -> 3, same 71 -> 72
p = R + r'\tests\Cybersole.Tests\OriginalViewClassParityTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        "GroupGrid",                // group rows are built inline inside the two pages''',
'''        // R210: GroupGrid is built. Proxies, Accounts and Billing all draw the same rail row (name, muted count,
        // tinted selection, "No groups matched your search"); it is one control now, and ProxyView uses it.''')
t = t.replace('''        Assert.Equal(71, same);          // R209: EmptyView left the debt''',
'''        Assert.Equal(72, same);          // R210: GroupGrid left the debt''')
t = t.replace('''        Assert.Equal(4, notBuilt);''', '''        Assert.Equal(3, notBuilt);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('parity buckets: same=72 notBuilt=3')

# guide + parity doc: UI classes 93 -> 94, UserControl 55 -> 56
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 93 个，**36 个不可达**（39%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 94 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide: 94')
