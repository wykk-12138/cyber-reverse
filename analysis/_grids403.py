import io
# AccountGrid.Rows — the visible accounts, which is what Ordered() already computes
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs"
t1 = io.open(p1, encoding='utf-8').read()
anchor1 = '''    /// <summary>The rows in display order. Sorting is a view concern'''
add1 = '''    /// <summary>
    /// The accounts on screen, in display order (bound as <c>Rows</c>). Same list <see cref="Ordered"/> produces.
    /// </summary>
    public IReadOnlyList<Account> Rows => Ordered();

''' + anchor1
assert anchor1 in t1 and 'public IReadOnlyList<Account> Rows' not in t1
io.open(p1, 'w', encoding='utf-8', newline='').write(t1.replace(anchor1, add1, 1))
print('AccountGrid.Rows added')

# GroupGrid.Items / Store
p2 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\GroupGrid.cs"
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    /// <summary>The rows currently built, as <c>(name, badge)</c>. Read back by tests.</summary>'''
add2 = '''    /// <summary>The group keys currently shown (bound as <c>Items</c>), in the order they are drawn.</summary>
    public IReadOnlyList<string> Items { get; private set; } = Array.Empty<string>();

    /// <summary>Which store the list is scoped to, empty for all of them (bound as <c>Store</c>; read-only in the image).</summary>
    public string Store { get; private set; } = string.Empty;

''' + anchor2
assert anchor2 in t2 and 'public IReadOnlyList<string> Items' not in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(anchor2, add2, 1))
print('GroupGrid.Items / Store added')
