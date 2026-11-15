import io
# 1) MessageBoxDialog: the four bound members are constructor parameters today
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''public sealed class MessageBoxDialog : Window
{
    public MessageBoxDialog(string title, string message,'''
add = '''public sealed class MessageBoxDialog : Window
{
    // R253: the original binds these four on the dialog (analysis/xaml_bindings.json) instead of taking them as
    // constructor parameters. They are exposed here as members and the constructor keeps its parameters for the existing
    // call sites, so both shapes work and there is still one place that decides what the buttons say.

    /// <summary>Label of the confirm button (bound as <c>ActionText</c>).</summary>
    public string ActionText { get; set; } = "OK";

    /// <summary>Label of the cancel button (bound as <c>CancelText</c>).</summary>
    public string CancelText { get; set; } = "Cancel";

    /// <summary>Whether the confirm button is shown (bound as <c>ShowAction</c>).</summary>
    public bool ShowAction { get; set; } = true;

    /// <summary>Whether the cancel button is shown (bound as <c>ShowCancel</c>).</summary>
    public bool ShowCancel { get; set; }

    public MessageBoxDialog(string title, string message,'''
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('MessageBoxDialog four members')

# 2) ProfileCreatorView: IsBulk / IsCreating / ShippingView / Summary
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''public sealed class ProfileCreatorView : UserControl
{
    private readonly AppServices _services;'''
add2 = '''public sealed class ProfileCreatorView : UserControl
{
    // R253: the original binds these on ProfileCreatorView (analysis/xaml_bindings.json).

    /// <summary>Whether the creator is in bulk mode (bound as <c>IsBulk</c>).</summary>
    public bool IsBulk { get; set; }

    /// <summary>False once the profile exists — the creator is "creating" until it is saved (bound as <c>IsCreating</c>).</summary>
    public bool IsCreating => !_saved;

    /// <summary>Whether the shipping section is showing (bound as <c>ShippingView</c>).</summary>
    public bool ShippingView { get; set; } = true;

    /// <summary>The one-line summary the dialog prints (bound as <c>Summary</c>).</summary>
    public string Summary => _summary.Text ?? string.Empty;

    private bool _saved;

    private readonly AppServices _services;'''
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ProfileCreatorView four members')
