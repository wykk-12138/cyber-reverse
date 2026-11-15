import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

# AppearanceView.ResetDefaults — the button already did this inline
old = '''        var reset = UiKit.Button("Reset Defaults", () =>'''
new = '''        // R243: the button's work is a named command now — the original binds ResetDefaults on this page
        // (analysis/xaml_bindings.json), and the page's own preview caption promises the button by that name.
        var reset = UiKit.Button("Reset Defaults", () =>'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    public AppearanceView(AppServices services)'''
add = '''    /// <summary>Restores the scrollbar defaults (bound as <c>ResetDefaults</c>).</summary>
    public void ResetDefaults()
    {
        var s = _appearanceServices?.Config.Settings;
        if (s is null) return;

        s.ScrollbarWidth = 10;
        s.ScrollbarCornerRadius = 6;
        s.ScrollbarColor = "#FFFFFF";
        _appearanceServices!.Config.Save();
        _appearanceStatus?.SetText("Scrollbar settings reset.");
    }

    private AppServices? _appearanceServices;
    private IStatusText? _appearanceStatus;

    /// <summary>Minimal status sink so <see cref="ResetDefaults"/> can report without a control reference.</summary>
    public interface IStatusText { void SetText(string text); }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AppearanceView.ResetDefaults added')
