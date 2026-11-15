import io
R = r'D:\projects\cyber-reverse\replica'

# CustomBrowser is built -> notBuilt 1 -> 0, same 74 -> 75
p = R + r'\tests\Cybersole.Tests\OriginalViewClassParityTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        "CustomBrowser",            // BrowserShim has no window; nothing renders a browser surface''',
'''        // R215: CustomBrowser is built — a window with the image's Browser.* chrome that drives the CDP session
        // through delegates. Nothing is left on this list.''')
t = t.replace('''        Assert.Equal(74, same);          // R214: SplashWindow left the debt''',
'''        Assert.Equal(75, same);          // R215: CustomBrowser left the debt — the list is now empty''')
t = t.replace('''        Assert.Equal(1, notBuilt);''', '''        Assert.Equal(0, notBuilt);''')
t = t.replace('''        Assert.Contains("CustomBrowser", NotBuiltYet);''',
'''        // R215: the last hole closed. Every original view class now has a counterpart.
        Assert.Empty(NotBuiltYet);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('parity: same=75 notBuilt=0')

# guide + parity doc: UI classes 96 -> 97, Window 25 -> 26
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 96 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 97 个，**36 个不可达**（37%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)

p3 = R + r'\docs\PARITY.md'
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace('**82 个 UI 类：25 个 `Window` 子类 + 57 个 `UserControl` 子类。**',
                '**83 个 UI 类：26 个 `Window` 子类 + 57 个 `UserControl` 子类。**')
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('guide 97 / parity 26 Window')
