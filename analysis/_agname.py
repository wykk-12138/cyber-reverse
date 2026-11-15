import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountModals.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>The group name in the box (bound as <c>GroupName</c>).</summary>
    public string GroupName => _name.Text ?? string.Empty;'''
new = '''    /// <summary>
    /// The group name (bound as <c>GroupName</c>). The image exposes it with a setter too (see
    /// docs/BINDING_SHAPES.md), so writing it updates the box as well as the group.
    /// </summary>
    public string GroupName
    {
        get => _name.Text ?? string.Empty;
        set
        {
            _name.Text = value ?? string.Empty;
            if (_group is not null) _group.Name = _name.Text!;
        }
    }'''
assert old in t
t = t.replace(old, new, 1)
# make sure the group is kept (ctor currently only stores the name)
t = t.replace('''    private readonly TextBox _name;

    public AccountGroupView(AccountGroup group)
    {''', '''    private readonly TextBox _name;
    private readonly AccountGroup? _group;

    public AccountGroupView(AccountGroup group)
    {
        _group = group;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('GroupName is now settable')
