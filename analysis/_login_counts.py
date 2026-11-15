import io
R = r'D:\projects\cyber-reverse\replica'

# LoginControl is built -> notBuilt 3 -> 2, same 72 -> 73
p = R + r'\tests\Cybersole.Tests\OriginalViewClassParityTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        "LoginControl",             // sign-in is a button on the toolbar, there is no login view''',
'''        // R213: LoginControl is built. The account window now opens it; every line it prints is an Auth.* key the
        // original ships, which is why the control needed no invented copy.''')
t = t.replace('''        Assert.Equal(72, same);          // R210: GroupGrid left the debt''',
'''        Assert.Equal(73, same);          // R213: LoginControl left the debt''')
t = t.replace('''        Assert.Equal(3, notBuilt);''', '''        Assert.Equal(2, notBuilt);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('parity: same=73 notBuilt=2')

# guide: UI classes 94 -> 95
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 94 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 95 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide: 95')
