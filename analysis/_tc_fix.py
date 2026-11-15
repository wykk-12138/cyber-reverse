import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''    /// <summary>Every profile the user has (bound as <c>ProfileItems</c>).</summary>
    public IReadOnlyList<Profile> ProfileItems => _services.Config.Profiles;

    /// <summary>The profile groups (bound as <c>ProfileGroupItems</c>).</summary>
    public IReadOnlyList<ProfileGroup> ProfileGroupItems => _services.Config.ProfileGroups;''',
'''    /// <summary>
    /// Every profile the user has, flattened across the profile groups (bound as <c>ProfileItems</c>).
    /// The profile groups are the Billing page's left rail — <c>Config.BillingGroups</c>.
    /// </summary>
    public IReadOnlyList<Profile> ProfileItems =>
        _services.Config.BillingGroups.SelectMany(g => g.Profiles).ToList();

    /// <summary>The profile groups (bound as <c>ProfileGroupItems</c>).</summary>
    public IReadOnlyList<BillingGroup> ProfileGroupItems => _services.Config.BillingGroups;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('profile sources corrected to billing groups')
