import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t = io.open(p, encoding='utf-8').read()

# the real APIs: ExpressionEngine.Evaluate for the test, and the list box holds strings
t = t.replace('        var result = Cybersole.Core.Profiles.ProfileGenerator.Generate(template);',
              '        var result = ExpressionEngine.Evaluate(template ?? string.Empty);', 1)

old_move = '''    /// <summary>Moves the selected profiles into another group (bound as <c>MoveGroup</c>). Returns how many moved.</summary>
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
    }'''
new_move = '''    /// <summary>
    /// Moves the profile at <paramref name="index"/> in the current list into another group (bound as <c>MoveGroup</c>).
    /// Returns the profile's new group id, or null when the move could not happen.
    /// </summary>
    public string? MoveGroup(int index, string targetGroupId)
    {
        if (string.IsNullOrWhiteSpace(targetGroupId)) return null;

        var target = _services.Config.BillingGroups.FirstOrDefault(g => g.Id == targetGroupId);
        if (target is null) return null;

        var current = CurrentGroup();
        if (current is null || index < 0 || index >= current.Profiles.Count) return null;

        var profile = current.Profiles[index];
        current.Profiles.RemoveAt(index);
        target.Profiles.Add(profile);
        _services.Config.Save();
        Refresh();
        _status.Text = $"Moved {profile.Name} to {target.Name}.";
        return target.Id;
    }

    /// <summary>The group the picker has selected.</summary>
    private BillingGroup? CurrentGroup()
    {
        var index = _groups.SelectedIndex;
        var groups = _services.Config.BillingGroups;
        return index >= 0 && index < groups.Count ? groups[index] : groups.FirstOrDefault();
    }'''
assert old_move in t
t = t.replace(old_move, new_move, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CreateTest/MoveGroup use the real APIs')
