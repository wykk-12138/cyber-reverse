import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()

old = '''    /// <summary>Reloads the number, the chart, the release carousel and the feed for the current period.</summary>
    public void LoadAnalytics()
    {'''
new = '''    /// <summary>Reloads the number, the chart, the release carousel and the feed for the current period.</summary>
    /// <remarks>
    /// R206: this rebuilds live <c>Children</c> collections. Called from a segmented control's handler while another
    /// thread is measuring the same view, Avalonia answers "Operations that change non-concurrent collections must have
    /// exclusive access" — measured one suite run in eight. The rebuild is posted to the UI thread when the caller is
    /// not on it, so the collections are only ever touched from the thread that owns them.
    /// </remarks>
    public void LoadAnalytics()
    {
        if (!Avalonia.Threading.Dispatcher.UIThread.CheckAccess())
        {
            Avalonia.Threading.Dispatcher.UIThread.Post(LoadAnalytics);
            return;
        }
'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('patched LoadAnalytics')
