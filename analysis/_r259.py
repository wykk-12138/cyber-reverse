import io

# 1) GroupGrid.DeleteGroup + a delete hook
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\GroupGrid.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    public void SetRows(IEnumerable<(string Name, string Badge)> rows) =>'''
add = '''    /// <summary>Raised when the bound command asks to delete the selected group (bound as <c>DeleteGroup</c>).</summary>
    public Action<string>? DeleteRequested { get; set; }

    /// <summary>
    /// Asks the owner to delete the selected group (bound as <c>DeleteGroup</c> on the accounts rail). The grid does not
    /// own the document, so it reports which key was selected and lets the caller remove it. Returns false when nothing
    /// is selected or no handler is bound.
    /// </summary>
    public bool DeleteGroup()
    {
        if (DeleteRequested is null) return false;
        var selected = SelectedKey;
        if (string.IsNullOrWhiteSpace(selected)) return false;

        DeleteRequested(selected!);
        return true;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GroupGrid.DeleteGroup + hook')

# 2) UserView.LogOut
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    public const string DashboardUrl = "https://cybersole.io/dashboard";'''
add2 = '''    public const string DashboardUrl = "https://cybersole.io/dashboard";

    /// <summary>The services this window acts on (bound as <c>LogOut</c> uses it).</summary>
    private AppServices? _services;

    /// <summary>Signs the session out and closes the window (bound as <c>LogOut</c>).</summary>
    public async Task<bool> LogOutAsync()
    {
        if (_services is null) return false;

        await _services.Session.SignOutAsync().ConfigureAwait(true);
        Close();
        return true;
    }'''
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
old_ctor = '''    public UserView(AppServices services)
    {
        Title = "Account";'''
new_ctor = '''    public UserView(AppServices services)
    {
        _services = services;
        Title = "Account";'''
assert old_ctor in t2
t2 = t2.replace(old_ctor, new_ctor, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('UserView.LogOutAsync')

# 3) CreateGroupModal.Types
p3 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountModals.cs'
t3 = io.open(p3, encoding='utf-8').read()
anchor3 = '''    private readonly ComboBox _type;'''
add3 = '''    /// <summary>The account types this dialog offers (bound as <c>Types</c>).</summary>
    public IReadOnlyList<string> Types => StoreCatalog.Platforms;

    private readonly ComboBox _type;'''
assert anchor3 in t3
t3 = t3.replace(anchor3, add3, 1)
io.open(p3, 'w', encoding='utf-8', newline='').write(t3)
print('CreateGroupModal.Types')

# 4) CaptchaProviderCreatorView.Creating + CloudflareSolverCreatorView.Creating
p4 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs'
t4 = io.open(p4, encoding='utf-8').read()
for cls in ('CaptchaProviderCreatorView', 'CloudflareSolverCreatorView'):
    anchor4 = 'public sealed class %s : SettingsModal\n{' % cls
    assert anchor4 in t4, cls
    add4 = anchor4 + '''

    /// <summary>True while this dialog is creating a new provider rather than editing one (bound as <c>Creating</c>).</summary>
    public bool Creating { get; private set; }'''
    t4 = t4.replace(anchor4, add4, 1)

t4 = t4.replace('''    public CaptchaProviderCreatorView(AppServices services, CaptchaProviderConfig? existing = null)
        : base(existing is null ? "New captcha provider" : $"Edit {existing.Name}", 520, 500)
    {
        var registry = services.Captcha.Registry;''',
'''    public CaptchaProviderCreatorView(AppServices services, CaptchaProviderConfig? existing = null)
        : base(existing is null ? "New captcha provider" : $"Edit {existing.Name}", 520, 500)
    {
        Creating = existing is null;
        var registry = services.Captcha.Registry;''', 1)
io.open(p4, 'w', encoding='utf-8', newline='').write(t4)
print('Creating flags')
