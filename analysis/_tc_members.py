import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs'
t = io.open(p, encoding='utf-8').read()

# keep the tab control so ShowCartView can report/select the Cart tab
t = t.replace('        var tabs = new TabControl { Height = 520 };',
              '        var tabs = new TabControl { Height = 520 };\n        _tabs = tabs;   // R233: ShowCartView reads the selected tab', 1)

anchor = '''    // ── Cart ──────────────────────────────────────────────────────────────────'''
add = '''    // ── bound members (R233) ─────────────────────────────────────────────────
    //
    // The original binds these on TaskCreatorMainView (analysis/xaml_bindings.json):
    //   ProfileGroupItems, ProfileItems, ShowCartView, SizeItems
    // The three lists are what the setup/cart tabs offer; ShowCartView is which tab is showing.

    private TabControl? _tabs;

    /// <summary>The size chips on offer (bound as <c>SizeItems</c>).</summary>
    public IReadOnlyList<string> SizeItems =>
        Cybersole.Core.Models.SizePalette.Build(_services.Config.Settings.CustomSizes);

    /// <summary>Every profile the user has (bound as <c>ProfileItems</c>).</summary>
    public IReadOnlyList<Profile> ProfileItems => _services.Config.Profiles;

    /// <summary>The profile groups (bound as <c>ProfileGroupItems</c>).</summary>
    public IReadOnlyList<ProfileGroup> ProfileGroupItems => _services.Config.ProfileGroups;

    /// <summary>True while the Cart tab is the selected one (bound as <c>ShowCartView</c>).</summary>
    public bool ShowCartView
    {
        get => _tabs?.SelectedIndex == 1;
        set
        {
            if (_tabs is null || !value) return;
            _tabs.SelectedIndex = 1;
        }
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('TaskCreatorView bound members added')
