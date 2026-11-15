import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\UtilitiesViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>
    /// Removes a store from the group being edited (bound as <c>RemoveStore</c>).'''
add = '''    /// <summary>
    /// Whether this dialog is editing an existing group rather than creating one (bound as <c>IsEditing</c>). Read-only: it
    /// is decided by the constructor argument.
    /// </summary>
    public bool IsEditing => _editing is not null;

    /// <summary>
    /// Deletes the group being edited from the configuration (bound as <c>Delete</c>). False when this dialog is creating a
    /// new group, or when the group was not in the list.
    /// </summary>
    public bool Delete()
    {
        if (_editing is null) return false;

        if (!Config.StoreGroups.Remove(_editing)) return false;

        Config.Save();
        return true;
    }

''' + anchor
assert anchor in t and 'public bool IsEditing' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('StoreGroupModal gains IsEditing + Delete')
