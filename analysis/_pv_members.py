import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

old = '''        var profileChoices = new[] { "Browser default" }
            .Concat(s.BrowserProfiles).Distinct().ToList();
        var checkoutProfile = UiKit.Combo(profileChoices, 0);'''
new = '''        var profileChoices = new[] { "Browser default" }
            .Concat(s.BrowserProfiles).Distinct().ToList();
        var checkoutProfile = UiKit.Combo(profileChoices, 0);
        _checkoutProfile = checkoutProfile;   // R238: SelectedProfiles reads it'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    public PaymentView(AppServices services)'''
add = '''    // ------------------------------------------------ bound members (R238)
    //
    // The original binds DetectedProfiles / SelectedProfiles on PaymentView (analysis/xaml_bindings.json).
    // Detected is what BrowserProfileScanner found and stored; Selected is what the Checkout Profiles combo holds.

    private ComboBox? _checkoutProfile;

    /// <summary>The browser profiles detected on this machine (bound as <c>DetectedProfiles</c>).</summary>
    public IReadOnlyList<string> DetectedProfiles => _services.Config.Settings.BrowserProfiles;

    /// <summary>The checkout profile currently chosen (bound as <c>SelectedProfiles</c>).</summary>
    public IReadOnlyList<string> SelectedProfiles
    {
        get
        {
            var choice = _checkoutProfile?.SelectedItem as string;
            return string.IsNullOrWhiteSpace(choice) ? Array.Empty<string>() : new[] { choice };
        }
    }

    /// <summary>Re-scans the machine for browser profiles (what the Refresh button does).</summary>
    public IReadOnlyList<string> RescanProfiles()
    {
        var found = Cybersole.Services.BrowserProfileScanner.Scan();
        if (found.Count == 0) return found;

        _services.Config.Settings.BrowserProfiles = found;
        _services.Config.Save();
        return found;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('PaymentView bound members added')
