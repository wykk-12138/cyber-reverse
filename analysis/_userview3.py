import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()
t = t.replace('Text = user?.DisplayName ?? user?.Email ?? "(signed out)",',
              'Text = user?.Email is { Length: > 0 } mail ? mail.Split(\'@\')[0] : "(signed out)",')
# the two link URLs are not in any evidence; declare them here and say so
t = t.replace('    public const string DashboardUrl = "https://cybersole.io/dashboard";',
              '''    public const string DashboardUrl = "https://cybersole.io/dashboard";

    /// <summary>inferred: no image evidence (R337) — the live panel has the button, not the URL.</summary>
    public const string TermsUrl = "https://cybersole.io/terms";

    /// <summary>inferred: no image evidence (R337).</summary>
    public const string PrivacyUrl = "https://cybersole.io/privacy";''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('fixed DisplayName + link URLs')
