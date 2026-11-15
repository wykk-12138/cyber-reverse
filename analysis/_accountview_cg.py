import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()

# 1) bound member instead of an inline lambda
old = '''        var newGroup = UiKit.Button("New Group", () =>
            CreateGroupModal.Show(this, StoreCatalog.Platforms[0], NameTaken, AddGroup));'''
new = '''        var newGroup = UiKit.Button("New Group", () => CreateGroup());'''
assert old in t
t = t.replace(old, new, 1)

# 2) expose it (the button and any caller now share one path)
anchor = '''        var newGroup = UiKit.Button("New Group", () => CreateGroup());'''
member = '''    /// <summary>
    /// Opens the "create account group" dialog for the first platform (bound as <c>CreateGroup</c>). The button that used to
    /// hold this inline now calls the member, so a keybind reaches the same place.
    /// </summary>
    public void CreateGroup() =>
        CreateGroupModal.Show(this, StoreCatalog.Platforms[0], NameTaken, AddGroup);

''' + anchor
t = t.replace(anchor, member, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AccountView.CreateGroup extracted')
