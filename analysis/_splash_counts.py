import io
# 1) rewrite the splash tests to use BuildVisual (no Window construction)
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SplashWindowTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''        var splash = new SplashWindow("5.18.32", "English");
        Assert.Equal("Version 5.18.32", splash.StatusText);

        _out.WriteLine(splash.StatusText);''',
'''        var (_, _, version) = SplashWindow.BuildVisual(en[SplashWindow.WelcomeKey], "5.18.32");
        Assert.Equal("Version 5.18.32", version.Text);

        _out.WriteLine(version.Text!);''')
t = t.replace('''        var splash = new SplashWindow();

        // the resource the original ships is Views/Auth/SplashWindow.axaml with these two names in it
        Assert.Equal("SplashBackground", splash.Background1.Name);
        var stack = Assert.IsType<Avalonia.Controls.StackPanel>(splash.Background1.Child);
        Assert.Contains(stack.Children.OfType<Avalonia.Controls.Border>(),
            b => b.Name == "SplashCyberIcon");''',
'''        var (background, stack, _) = SplashWindow.BuildVisual("Welcome to Cybersole 5.0", null);

        // the resource the original ships is Views/Auth/SplashWindow.axaml with these two names in it
        Assert.Equal("SplashBackground", background.Name);
        Assert.Same(stack, background.Child);
        Assert.Contains(stack.Children.OfType<Avalonia.Controls.Border>(),
            b => b.Name == "SplashCyberIcon");''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('splash tests use BuildVisual')

R = r'D:\projects\cyber-reverse\replica'
# 2) parity: SplashWindow is built -> notBuilt 2 -> 1, same 73 -> 74
p2 = R + r'\tests\Cybersole.Tests\OriginalViewClassParityTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''        "SplashWindow",             // no splash: the replica shows MainWindow straight away''',
'''        // R214: SplashWindow is built. The image carries its XAML resource name and the two control names inside it;
        // Program now shows it before the shell and closes it when MainWindow opens.''')
t2 = t2.replace('''        Assert.Equal(73, same);          // R213: LoginControl left the debt''',
'''        Assert.Equal(74, same);          // R214: SplashWindow left the debt''')
t2 = t2.replace('''        Assert.Equal(2, notBuilt);''', '''        Assert.Equal(1, notBuilt);''')
t2 = t2.replace('''        Assert.Contains("SplashWindow", NotBuiltYet);
        Assert.Contains("CustomBrowser", NotBuiltYet);''',
'''        Assert.Contains("CustomBrowser", NotBuiltYet);''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('parity: same=74 notBuilt=1')

# 3) guide + parity doc: UI classes 95 -> 96, Window 24 -> 25
p3 = R + r'\docs\VERDICT.md'
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace('| UI 类 | 95 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 96 个，**36 个不可达**（38%） | `UnreachedUiTypesTests` |')
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)

p4 = R + r'\docs\PARITY.md'
t4 = io.open(p4, encoding='utf-8').read()
t4 = t4.replace('**81 个 UI 类：24 个 `Window` 子类 + 57 个 `UserControl` 子类。**',
                '**82 个 UI 类：25 个 `Window` 子类 + 57 个 `UserControl` 子类。**')
io.open(p4, 'w', encoding='utf-8', newline='').write(t4)
print('guide 96 / parity 25 Window')
