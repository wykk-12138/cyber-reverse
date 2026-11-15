import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>The profiles on the page (bound as <c>Groups</c>… no: the group names the combo lists).</summary>
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
'''
new = '''    /// <summary>The billing-group names the combo lists (bound as <c>Groups</c>).</summary>
    public IReadOnlyList<string> Groups =>
        _services.Config.BillingGroups.Select(g => g.Name).ToList();

    /// <summary>
    /// Deletes the profile selected in the list and saves (bound as <c>DeleteSelected</c>). The list the page shows is the
    /// selected billing group's profiles, so that is where the removal happens.
    /// </summary>
    public bool DeleteSelected()
    {
        var index = _profiles.SelectedIndex;
        var group = CurrentGroup();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        group.Profiles.RemoveAt(index);
        _services.Config.Save();
        ShowGroup(group);
        return true;
    }

    /// <summary>Opens the editor for the profile selected in the list (bound as <c>EditSelected</c>).</summary>
    public bool EditSelected()
    {
        var index = _profiles.SelectedIndex;
        var group = CurrentGroup();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        OpenProfileEditor(group.Profiles[index]);
        return true;
    }

    /// <summary>The billing group the combo currently shows, by index into the configuration.</summary>
    private BillingGroup? CurrentGroup()
    {
        var groups = _services.Config.BillingGroups;
        var index = _groups.SelectedIndex;
        return index >= 0 && index < groups.Count ? groups[index] : null;
    }
'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('ProfileView members rewritten against the real data source')
