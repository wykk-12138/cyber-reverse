import io, re
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

start = t.index('public sealed class WebhookCreatorView')
end = t.index('BuildFooter(SaveButton(', start)
seg = t[start:end]

# swap the footer button for one whose label follows the name box, as the live modal shows ("Enter name")
add = '''// R339: the live modal's submit button reads "Enter name" while the name box is empty; the filled-state label is
    // inferred (the only state the running build showed was the empty one).
    private Button _submit = null!;
    private TextBox _nameBox = null!;

'''
seg = seg.replace('    public WebhookCreatorView(AppServices services)', add + '    public WebhookCreatorView(AppServices services)', 1)
t = t[:start] + seg + t[end:]

old = '''        BuildFooter(SaveButton(() =>'''
new = '''        _nameBox = name;
        _submit = UiKit.Button("Enter name", Save);
        name.TextChanged += (_, _) => _submit.Content = string.IsNullOrWhiteSpace(name.Text) ? "Enter name" : "Create";
        BuildFooter(_submit);

        void Save() => SaveCore();'''
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('submit button label wired (stub)')
