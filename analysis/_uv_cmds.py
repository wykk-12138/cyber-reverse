import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs'
t = io.open(p, encoding='utf-8').read()

# the four bound commands, with the behaviour that already existed in the lambdas
anchor = '''    private StoreGroup? Selected()'''
add = '''    // ------------------------------------------------ bound commands (R231)
    //
    // The original binds these five members on UtilitiesView (analysis/xaml_bindings.json):
    //   CloneStoreGroup, CreateStoreGroup, DeleteStoreGroup, EditStoreGroup, StoreGroups
    // The behaviour existed inside the "New / Clone / Delete" lambdas; the names are what a keybind or a rebinding
    // addresses, so they exist here and the buttons call them.

    /// <summary>The store groups on screen (bound as <c>StoreGroups</c>).</summary>
    public IReadOnlyList<StoreGroup> StoreGroups => _services.Config.Settings.StoreGroups;

    /// <summary>Creates a group, named from <paramref name="name"/> or "Group N" (bound as <c>CreateStoreGroup</c>).</summary>
    public StoreGroup CreateStoreGroup(string? name)
    {
        var group = new StoreGroup
        {
            Name = string.IsNullOrWhiteSpace(name)
                ? $"Group {_services.Config.Settings.StoreGroups.Count + 1}"
                : name!.Trim(),
        };
        _services.Config.Settings.StoreGroups.Add(group);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group created.";
        return group;
    }

    /// <summary>Duplicates the selected group (bound as <c>CloneStoreGroup</c>).</summary>
    public StoreGroup? CloneStoreGroup()
    {
        var src = Selected();
        if (src is null) return null;

        var copy = new StoreGroup
        {
            Name = src.Name + " copy",
            Enabled = src.Enabled,
            Stores = src.Stores.ToList(),
        };
        _services.Config.Settings.StoreGroups.Add(copy);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group cloned.";
        return copy;
    }

    /// <summary>Removes the selected group (bound as <c>DeleteStoreGroup</c>).</summary>
    public bool DeleteStoreGroup()
    {
        var target = Selected();
        if (target is null) return false;

        _services.Config.Settings.StoreGroups.Remove(target);
        _services.Config.Save();
        Refresh();
        _status.Text = "Group deleted.";
        return true;
    }

    /// <summary>Opens the group editor for the selection (bound as <c>EditStoreGroup</c>).</summary>
    public void EditStoreGroup()
    {
        var existing = Selected();
        if (TopLevel.GetTopLevel(this) is Window owner)
            _ = new StoreGroupModal(_services, existing).ShowDialog(owner);
        else if (existing is not null)
            _status.Text = "No window host to edit " + existing.Name;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# the three buttons now call the commands
t = t.replace('''            UiKit.Button("New", () =>
            {
                _services.Config.Settings.StoreGroups.Add(new StoreGroup
                {
                    Name = string.IsNullOrWhiteSpace(name.Text)
                        ? $"Group {_services.Config.Settings.StoreGroups.Count + 1}"
                        : name.Text!,
                });
                _services.Config.Save();
                Refresh();
                _status.Text = "Group created.";
            }),
            UiKit.Button("Clone", () =>
            {
                var src = Selected();
                if (src is null) return;
                _services.Config.Settings.StoreGroups.Add(new StoreGroup
                {
                    Name = src.Name + " copy",
                    Enabled = src.Enabled,
                    Stores = src.Stores.ToList(),
                });
                _services.Config.Save();
                Refresh();
                _status.Text = "Group cloned.";
            }),
            UiKit.Button("Delete", () =>
            {
                var target = Selected();
                if (target is null) return;
                _services.Config.Settings.StoreGroups.Remove(target);
                _services.Config.Save();
                Refresh();
                _status.Text = "Group deleted.";
            })));''',
'''            UiKit.Button("New", () => CreateStoreGroup(name.Text)),
            UiKit.Button("Clone", () => CloneStoreGroup()),
            UiKit.Button("Delete", () => DeleteStoreGroup())));''')

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('UtilitiesView bound commands added and wired')
