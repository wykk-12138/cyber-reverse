import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding='utf-8').read()

bad = '''        _nameBox = name;
        _submit = UiKit.Button("Enter name", Save);
        name.TextChanged += (_, _) => _submit.Content = string.IsNullOrWhiteSpace(name.Text) ? "Enter name" : "Create";
        BuildFooter(_submit);

        void Save() => SaveCore();'''
assert bad in t
t = t.replace(bad, '        BuildFooter(SaveButton(() =>', 1)

stub = '''// R339: the live modal's submit button reads "Enter name" while the name box is empty; the filled-state label is
    // inferred (the only state the running build showed was the empty one).
    private Button _submit = null!;
    private TextBox _nameBox = null!;

'''
assert stub in t
t = t.replace(stub, '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('reverted the button stub; layout changes kept')
