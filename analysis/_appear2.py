import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

# simplify: no status sink, no unused interface
old_block = '''    /// <summary>Restores the scrollbar defaults (bound as <c>ResetDefaults</c>).</summary>
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
'''
new_block = '''    /// <summary>Restores the scrollbar defaults (bound as <c>ResetDefaults</c>).</summary>
    public void ResetDefaults()
    {
        var s = _appearanceServices?.Config.Settings;
        if (s is null) return;

        s.ScrollbarWidth = 10;
        s.ScrollbarCornerRadius = 6;
        s.ScrollbarColor = "#FFFFFF";
        _appearanceServices!.Config.Save();
    }

    private AppServices? _appearanceServices;
'''
assert old_block in t
t = t.replace(old_block, new_block, 1)

# the constructor keeps services, and the button goes through the command
t = t.replace('''    public AppearanceView(AppServices services)
    {
        var s = services.Config.Settings;''',
'''    public AppearanceView(AppServices services)
    {
        _appearanceServices = services;
        var s = services.Config.Settings;''', 1)

old_btn = '''        var reset = UiKit.Button("Reset Defaults", () =>
        {
            s.ScrollbarWidth = 10;
            s.ScrollbarCornerRadius = 6;
            s.ScrollbarColor = "#FFFFFF";'''
new_btn = '''        var reset = UiKit.Button("Reset Defaults", () =>
        {
            ResetDefaults();'''
assert old_btn in t
t = t.replace(old_btn, new_btn, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ResetDefaults wired to the button')
