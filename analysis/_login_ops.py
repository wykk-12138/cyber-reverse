import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Auth\LoginControl.cs"
t = io.open(p, encoding='utf-8').read()

# 1) name the five operations the binding table binds, keeping the inline behaviour as their bodies
anchor = '''    private void StartBrowserSignIn()'''
add = '''    // ── the five operations the image binds on this control (R343) ──────────────────────────────────────
    // Cybersole.Ui.Views.Auth.LoginControl -> Cancel, OpenBrowser, SignIn, SignUp, UseCode.
    // The work used to sit in inline lambdas, which is the same code with no name to bind to.

    /// <summary>Hides the waiting block and reports a denied sign-in (bound as <c>Cancel</c>).</summary>
    public void Cancel()
    {
        _waiting.IsVisible = false;
        _status.Text = _loc["Auth.Login.Error.Denied"];
    }

    /// <summary>Opens the sign-in page in the default browser (bound as <c>OpenBrowser</c>).</summary>
    public void OpenBrowser() => StartBrowserSignIn();

    /// <summary>Runs the credential/code sign-in and returns whether it succeeded (bound as <c>SignIn</c>).</summary>
    public async Task<bool> SignInAsync(string code)
    {
        _status.Text = _loc["Auth.Login.Waiting"];
        var ok = await _services.Auth.ExchangeCodeAsync(code).ConfigureAwait(true);
        _status.Text = ok ? _loc["Auth.License.SelectPrompt"] : _loc["Auth.Login.Error.Failed"];
        if (ok) SignedIn?.Invoke(this, EventArgs.Empty);
        return ok;
    }

    /// <summary>Opens the account-creation page (bound as <c>SignUp</c>).</summary>
    public void SignUp() => OpenUrl(AuthService.WebBase + "/signup");

    /// <summary>Swaps the waiting block for the code entry (bound as <c>UseCode</c>).</summary>
    public void UseCode()
    {
        _codeForm.IsVisible = true;
        _waiting.IsVisible = false;
        _status.Text = _loc["Auth.Login.CodePrompt"];
    }

    private void StartBrowserSignIn()'''
assert anchor in t
t = t.replace(anchor, add, 1)

# 2) the buttons call the named methods
t = t.replace('''        var useCode = new Button { Content = _loc["Auth.Login.UseCode"], Background = Brushes.Transparent };
        useCode.Click += (_, _) =>
        {
            _codeForm.IsVisible = true;
            _waiting.IsVisible = false;
            _status.Text = _loc["Auth.Login.CodePrompt"];
        };''',
'''        var useCode = new Button { Content = _loc["Auth.Login.UseCode"], Background = Brushes.Transparent };
        useCode.Click += (_, _) => UseCode();''', 1)

t = t.replace('''        var cancel = UiKit.Button(_loc["Auth.Login.Cancel"], () =>
        {
            _waiting.IsVisible = false;
            _status.Text = _loc["Auth.Login.Error.Denied"];
        });''',
'''        var cancel = UiKit.Button(_loc["Auth.Login.Cancel"], Cancel);''', 1)

t = t.replace('''            _status.Text = _loc["Auth.Login.Waiting"];
            var ok = await _services.Auth.ExchangeCodeAsync(entry.Text ?? string.Empty).ConfigureAwait(true);
            _status.Text = ok ? _loc["Auth.License.SelectPrompt"] : _loc["Auth.Login.Error.Failed"];
            if (ok) SignedIn?.Invoke(this, EventArgs.Empty);''',
'''            await SignInAsync(entry.Text ?? string.Empty).ConfigureAwait(true);''', 1)

t = t.replace('''        signUp.Click += (_, _) => OpenUrl(AuthService.WebBase + "/signup");''',
'''        signUp.Click += (_, _) => SignUp();''', 1)

if 'using System.Threading.Tasks;' not in t:
    t = t.replace('using System.Diagnostics;', 'using System.Diagnostics;\nusing System.Threading.Tasks;', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('five named operations extracted')
