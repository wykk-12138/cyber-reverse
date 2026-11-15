import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>Opens the group editor (bound as <c>CreateGroup</c>).</summary>'''
add = '''    /// <summary>The profiles on the page (bound as <c>Groups</c>… no: the group names the combo lists).</summary>
    public IReadOnlyList<string> Groups =>
        _groups.ItemsSource?.Cast<string>().ToList() ?? new List<string>();

    /// <summary>Deletes the profile selected in the list and saves (bound as <c>DeleteSelected</c>).</summary>
    public bool DeleteSelected()
    {
        var index = _profiles.SelectedIndex;
        var profiles = _services.Config.Profiles;
        if (index < 0 || index >= profiles.Count) return false;

        profiles.RemoveAt(index);
        _services.Config.Save();
        Refresh();
        return true;
    }

    /// <summary>Opens the editor for the profile selected in the list (bound as <c>EditSelected</c>).</summary>
    public bool EditSelected()
    {
        var index = _profiles.SelectedIndex;
        var profiles = _services.Config.Profiles;
        if (index < 0 || index >= profiles.Count) return false;

        OpenProfileEditor(profiles[index]);
        return true;
    }

''' + anchor
assert anchor in t and 'public bool DeleteSelected()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ProfileView gains Groups/DeleteSelected/EditSelected')
