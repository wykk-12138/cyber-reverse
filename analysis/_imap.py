import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    public ImapView(AppServices services)'''
add = '''    // ------------------------------------------------ bound commands (R245)
    //
    // The original binds DisconnectAycd on ImapView (analysis/xaml_bindings.json): the page shows the AYCD inbox
    // connection state, so it also needs the way to drop it.

    private AppServices? _imapServices;

    /// <summary>
    /// Drops the AYCD inbox connection: clears the API key and switches the inbox off (bound as <c>DisconnectAycd</c>).
    /// Returns false when there was nothing connected.
    /// </summary>
    public bool DisconnectAycd()
    {
        var doc = _imapServices?.Config.Accounts;
        if (doc is null) return false;

        var aycd = doc.AycdInbox;
        if (string.IsNullOrEmpty(aycd.ApiKey) && !aycd.Enabled) return false;

        aycd.ApiKey = string.Empty;
        aycd.Enabled = false;
        _imapServices!.Config.Save();
        return true;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
t = t.replace('''    public ImapView(AppServices services)
    {
        var doc = services.Config.Accounts;''',
'''    public ImapView(AppServices services)
    {
        _imapServices = services;
        var doc = services.Config.Accounts;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ImapView.DisconnectAycd added')
