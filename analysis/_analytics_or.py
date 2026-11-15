import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    private readonly AppServices _services;'''
add = '''    /// <summary>
    /// Opens one release (bound as <c>OpenRelease</c>). <c>ReleaseView</c> existed with Previous / Release / ShowGuide /
    /// ShowSitelist and nothing constructed it; this is the page that opens it, so the dialog title is the release's own
    /// product name. False when there is no window to host it.
    /// </summary>
    public bool OpenRelease(Release release)
    {
        if (release is null || TopLevel.GetTopLevel(this) is not Window) return false;

        Views.Common.ViewHostModal.Show(this, release.Product ?? "Release", new ReleaseView(_services, release));
        return true;
    }

''' + anchor
assert anchor in t and 'public bool OpenRelease(' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('AnalyticsView.OpenRelease added')
