import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs'
t = io.open(p, encoding='utf-8').read()

# give EditMode a writer: it follows "editing an existing record"
old1 = '''    /// <summary>True when editing an existing account rather than creating one (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }'''
new1 = '''    /// <summary>True when editing an existing account rather than creating one (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

    /// <summary>Records whether this dialog is an edit (the constructor decides).</summary>
    private void SetEditMode(bool editing) => EditMode = editing;'''
t = t.replace(old1, new1, 1)

old2 = '''    /// <summary>True when editing an existing account (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }'''
new2 = '''    /// <summary>True when editing an existing account (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

    /// <summary>Records whether this dialog is an edit (the constructor decides).</summary>
    private void SetEditMode(bool editing) => EditMode = editing;'''
t = t.replace(old2, new2, 1)

# constructors call it, and the account-name field feeds AccountName
oldg = '''    public GoogleAccountEditView(AppServices services, GoogleAccount? existing = null)
        : base(existing is null ? "New Google account" : "Edit Google account", 480, 380)
    {
        var doc = services.Config.Accounts;'''
newg = '''    public GoogleAccountEditView(AppServices services, GoogleAccount? existing = null)
        : base(existing is null ? "New Google account" : "Edit Google account", 480, 380)
    {
        SetEditMode(existing is not null);
        AccountName = existing?.Name ?? string.Empty;
        var doc = services.Config.Accounts;'''
assert oldg in t
t = t.replace(oldg, newg, 1)

oldp = '''        var password = UiKit.Text(password: true, watermark: "paypal password");'''
if oldp in t:
    t = t.replace('        var doc = services.Config.Accounts;\n\n        var model = UiKit.Text(existing?.Email, watermark: "paypal email");',
                  '        SetEditMode(existing is not null);\n        InactivateAfter = existing?.MaxInactiveSessionDuration ?? "Permanent";\n        var doc = services.Config.Accounts;\n\n        var model = UiKit.Text(existing?.Email, watermark: "paypal email");', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('EditMode/AccountName/InactivateAfter wired in the constructors')
