import io

# 1) SmartActionsView.ViewLogs -> the history window that already exists
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '''    public SmartActionsView(AppServices services)
    {'''
add = '''    /// <summary>
    /// Shows the run history (bound as <c>ViewLogs</c>). The history window was already written; nothing opened it from
    /// this page.
    /// </summary>
    public void ViewLogs()
    {
        if (TopLevel.GetTopLevel(this) is Window owner) new HistoryWindow(_services).Show(owner);
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SmartActionsView.ViewLogs')

# 2) ReleaseView.ShowGuide -> ReleaseGuideView (declared but never constructed before this)
p2 = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
anchor2 = '''    public ReleaseView(AppServices services, Release? release = null)
    {
        _ = services;'''
add2 = '''    private readonly AppServices _releaseServices;

    /// <summary>
    /// Shows the buying guide for this release (bound as <c>ShowGuide</c>). R261: <c>ReleaseGuideView</c> existed and had
    /// never been constructed by anything.
    /// </summary>
    public bool ShowGuide()
    {
        if (TopLevel.GetTopLevel(this) is not Window owner) return false;
        new ReleaseGuideView(_releaseServices, _release) { }.Show(owner);
        return true;
    }

    public ReleaseView(AppServices services, Release? release = null)
    {
        _releaseServices = services;'''
assert anchor2 in t2
t2 = t2.replace(anchor2, add2, 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ReleaseView.ShowGuide')
