import io
# AnalyticsView: ChangeChart + OpenRelease
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    public AnalyticsView(AppServices services)
    {'''
add = '''    // ------------------------------------------------ bound commands (R254)
    //
    // The original binds ChangeChart / OpenRelease / MoveNext / MovePrevious on AnalyticsView
    // (analysis/xaml_bindings.json). The pager commands already exist; these two were missing.

    /// <summary>
    /// Switches the checkouts/spend segment (bound as <c>ChangeChart</c>). Returns false for an unknown segment name.
    /// </summary>
    public bool ChangeChart(string segment)
    {
        var index = Array.FindIndex(Segments, s => string.Equals(s, segment, StringComparison.OrdinalIgnoreCase));
        if (index < 0) return false;

        _segment = index;

        // changing the segment used to be a radio row; setting the field and reloading is the same effect
        if (index == 0) _caption.Text = "Checkouts"; else _caption.Text = "Money spent";
        Reload();
        return true;
    }

    /// <summary>How many charts the page can show (the segment names).</summary>
    public IReadOnlyList<string> Charts => Segments;

    /// <summary>
    /// Opens a release's page (bound as <c>OpenRelease</c>). Returns the url it asked the browser to open, or null when
    /// there is no such release or no browser is bound.
    /// </summary>
    public string? OpenRelease(string name)
    {
        var release = _services.Config.Analytics.Releases
            .FirstOrDefault(r => string.Equals(r.Name, name, StringComparison.OrdinalIgnoreCase));
        if (release is null) return null;

        var url = release.Url;
        if (string.IsNullOrWhiteSpace(url)) return null;

        _services.Browser.Open(url);
        return url;
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AnalyticsView.ChangeChart / OpenRelease added (draft)')

# AccountGrid: MoveGroup + OpenSettings
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    /// <summary>Copies the selected accounts (bound as <c>CopyAccounts</c>).</summary>'''
add2 = '''    /// <summary>Moves the selection to another group (bound as <c>MoveGroup</c>).</summary>
    public void MoveGroup() => MoveSelected();

    /// <summary>Opens Settings' account page (bound as <c>OpenSettings</c>).</summary>
    public bool OpenSettings()
    {
        if (TopLevel.GetTopLevel(this) is not MainWindow shell) return false;
        return shell.Navigate("Settings");
    }

''' + anchor2
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('AccountGrid.MoveGroup / OpenSettings added')
