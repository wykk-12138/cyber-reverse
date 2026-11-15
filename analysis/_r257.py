import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs'
t = io.open(p, encoding='utf-8').read()

# GoogleAccountEditView: AccountName + EditMode
anchor = '''public sealed class GoogleAccountEditView : SettingsModal
{'''
add = '''public sealed class GoogleAccountEditView : SettingsModal
{
    // R257: the original binds AccountName / EditMode here (analysis/xaml_bindings.json).

    /// <summary>The display name typed into the dialog (bound as <c>AccountName</c>).</summary>
    public string AccountName { get; set; } = string.Empty;

    /// <summary>True when editing an existing account rather than creating one (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

'''
assert anchor in t
t = t.replace(anchor, add, 1)

# PayPalAccountCreatorView: EditMode + InactivateAfter
anchor2 = '''public sealed class PayPalAccountCreatorView : SettingsModal
{'''
add2 = '''public sealed class PayPalAccountCreatorView : SettingsModal
{
    // R257: the original binds EditMode / InactivateAfter here (analysis/xaml_bindings.json).

    /// <summary>True when editing an existing account (bound as <c>EditMode</c>).</summary>
    public bool EditMode { get; private set; }

    /// <summary>The inactivity window after which the session is dropped (bound as <c>InactivateAfter</c>).</summary>
    public string InactivateAfter { get; set; } = "Permanent";

'''
assert anchor2 in t
t = t.replace(anchor2, add2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('two settings modals: four members declared')
