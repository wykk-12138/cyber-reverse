import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''    /// <summary>
    /// Shows the buying guide for this release (bound as <c>ShowGuide</c>).'''
add = '''    /// <summary>
    /// Shows the release's site list (bound as <c>ShowSitelist</c>). The locale names the tab — "Release.Tab.Sitelist" =
    /// "Sitelist" — and <c>ReleaseSitelistView</c> is that list, which nothing constructed until now.
    /// </summary>
    public bool ShowSitelist()
    {
        if (TopLevel.GetTopLevel(this) is not Window) return false;

        Views.Common.ViewHostModal.Show(this, "Sitelist", new ReleaseSitelistView(_releaseServices, _release));
        return true;
    }

''' + anchor
assert anchor in t and 'public bool ShowSitelist()' not in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('ReleaseView.ShowSitelist added')
