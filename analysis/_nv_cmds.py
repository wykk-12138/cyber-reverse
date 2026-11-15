import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    public NotificationsView(AppServices services)'''
add = '''    // ------------------------------------------------ bound commands (R239)
    //
    // The original binds SelectSound / ResetSound on NotificationsView (analysis/xaml_bindings.json).
    // The "Default / <file>" button and the "Reset" button below did this inline; the names are what a rebinding
    // addresses, so the work sits in methods and the buttons call them.

    private AppServices? _services;

    /// <summary>The sound path for a tab; empty means the platform default (bound as <c>SelectSound</c>).</summary>
    public string SelectSound(string tab, string path)
    {
        var options = OptionsFor(_services!.Config.Settings, tab);
        options.Path = path ?? string.Empty;
        _services.Config.Save();
        return options.Path;
    }

    /// <summary>Puts a tab back on the default sound (bound as <c>ResetSound</c>).</summary>
    public void ResetSound(string tab) => SelectSound(tab, string.Empty);

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)

# the constructor keeps services so the two commands can work
t = t.replace('''    public NotificationsView(AppServices services)
    {
        var s = services.Config.Settings;''',
'''    public NotificationsView(AppServices services)
    {
        _services = services;
        var s = services.Config.Settings;''', 1)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('NotificationsView bound commands added')
