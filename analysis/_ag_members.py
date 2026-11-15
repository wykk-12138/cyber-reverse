import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>
    /// <paramref name="accounts"/> is the live list, not a copy'''
add = '''    /// <summary>
    /// The account group these rows belong to, as the model records it (bound as <c>AccountGroup</c>; the image exposes it
    /// read-only). A grid is always shown for one group, so the first row's <c>GroupId</c> is the group's; empty when the
    /// grid has no rows.
    /// </summary>
    public string AccountGroup => _rows.FirstOrDefault()?.GroupId ?? string.Empty;

    /// <summary>
    /// Whether the grid is showing an existing group's accounts (bound as <c>Edit</c>, read-only in the image). True when the
    /// grid has rows, which is when an edit makes sense.
    /// </summary>
    public bool Edit => _rows.Count > 0;

''' + anchor
assert anchor in t and 'public string AccountGroup =>' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('AccountGrid.AccountGroup / Edit added')
