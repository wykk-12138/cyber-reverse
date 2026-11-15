import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    public ProfileView(AppServices services)
    {'''
add = '''    // ------------------------------------------------ bound commands (R250)
    //
    // The original binds CreateGroup / CreateTest / MoveGroup / OpenCreator / OpenCsvEditor / OpenSettings on
    // ProfileView (analysis/xaml_bindings.json). Every one of them was already reachable as a button or inline lambda;
    // the names are what a keybind or a rebinding addresses.

    /// <summary>Opens the group editor (bound as <c>CreateGroup</c>).</summary>
    public void CreateGroup() => ViewHostModal.Show(this, "Profile groups", new ProfileGroupView(_services));

    /// <summary>Opens the CSV editor (bound as <c>OpenCsvEditor</c>).</summary>
    public void OpenCsvEditor() =>
        ViewHostModal.Show(this, "CSV profile editor", new ProfileCsvEditorView(_services));

    /// <summary>Opens the profile creator for a new profile (bound as <c>OpenCreator</c>).</summary>
    public void OpenCreator() => OpenProfileEditor(null);

    /// <summary>
    /// Opens Settings' browser-profile page — the profiles this app checks out with are Chrome profiles
    /// (bound as <c>OpenSettings</c>).
    /// </summary>
    public bool OpenSettings()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

    /// <summary>Runs the generator test against the current template (bound as <c>CreateTest</c>).</summary>
    public string CreateTest(string template)
    {
        var result = Cybersole.Core.Profiles.ProfileGenerator.Generate(template);
        _status.Text = result;
        return result;
    }

    /// <summary>Moves the selected profiles into another group (bound as <c>MoveGroup</c>). Returns how many moved.</summary>
    public int MoveGroup(string targetGroupId)
    {
        if (string.IsNullOrWhiteSpace(targetGroupId)) return 0;

        var target = _services.Config.BillingGroups.FirstOrDefault(g => g.Id == targetGroupId);
        if (target is null) return 0;

        var selected = SelectedProfiles().ToList();
        if (selected.Count == 0) return 0;

        foreach (var profile in selected) MoveToGroup(profile, target);
        _services.Config.Save();
        Refresh();
        _status.Text = $"Moved {selected.Count} profile(s) to {target.Name}.";
        return selected.Count;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProfileView bound commands added (draft)')
