import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    private Control BuildSignIn()
    {
        var browser = UiKit.Button(_loc["Auth.Login.Button"], StartBrowserSignIn);
        var useCode = new Button { Content = _loc["Auth.Login.UseCode"], Background = Brushes.Transparent };
        useCode.Click += (_, _) => UseCode();

        var remember = new CheckBox { Content = _loc["Auth.Login.RememberMe"] };

        return new StackPanel
        {
            Spacing = 6,
            Children = { browser, useCode, remember },
        };
    }'''
new = '''    private Control BuildSignIn()
    {
        var browser = UiKit.Button(_loc["Auth.Login.Button"], StartBrowserSignIn);
        var remember = new CheckBox { Content = _loc["Auth.Login.RememberMe"] };

        // R381: the live 5.18.32 sign-in screen is exactly three things — "Sign in with browser", a "Remember Me"
        // checkbox and the "Don't have an account? Sign Up" line (measured on the running build). "Use a code instead"
        // belongs to the waiting state, not here; it is the escape hatch from the browser flow. Keeping it on the first
        // screen put a fourth control on a screen the image does not have one on.
        return new StackPanel
        {
            Spacing = 6,
            Children = { browser, remember },
        };
    }'''
assert old in t
t = t.replace(old, new, 1)

# the waiting state gains the escape hatch
t = t.replace('''        _waiting.Children.Add(_code);
        _waiting.Children.Add(UiKit.Buttons(again, cancel));''',
'''        _waiting.Children.Add(_code);

        // R381: "Use a code instead" lives here, beside the code entry it switches to
        var useCode = new Button { Content = _loc["Auth.Login.UseCode"], Background = Brushes.Transparent };
        useCode.Click += (_, _) => UseCode();
        _waiting.Children.Add(useCode);

        _waiting.Children.Add(UiKit.Buttons(again, cancel));''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('login screen now matches the measured three-control layout')
