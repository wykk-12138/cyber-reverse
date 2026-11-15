import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountView.cs"
t = io.open(p, encoding='utf-8').read()
bad = '''    /// <summary>
    /// Opens the "create account group" dialog for the first platform (bound as <c>CreateGroup</c>). The button that used to
    /// hold this inline now calls the member, so a keybind reaches the same place.
    /// </summary>
    public void CreateGroup() =>
        CreateGroupModal.Show(this, StoreCatalog.Platforms[0], NameTaken, AddGroup);

        var newGroup'''
good = '''        var newGroup'''
assert bad in t
t = t.replace(bad, good, 1)

# now put the member at class level: right before Build()'s sibling method — use the class's first method after fields
anchor = '''    private Control Build()'''
member = '''    /// <summary>
    /// Opens the "create account group" dialog for the first platform (bound as <c>CreateGroup</c>). The button that used to
    /// hold this inline now calls the member, so a keybind reaches the same place.
    /// </summary>
    public void CreateGroup() =>
        CreateGroupModal.Show(this, StoreCatalog.Platforms[0], NameTaken, AddGroup);

''' + anchor
assert anchor in t and 'public void CreateGroup()' not in t
t = t.replace(anchor, member, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('member moved to class level')
