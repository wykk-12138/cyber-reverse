import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) page count: zero when there are no releases — the live empty state prints "0 / 0" (R334)
old_pages = '''    /// <summary>How many pages the carousel has.</summary>
    public int ReleasePages => Math.Max(1, (_services.Stats.ByStoreInPeriod(CurrentPeriod.From, CurrentPeriod.To).Count + 2) / 3);'''
new_pages = '''    /// <summary>
    /// How many pages the carousel has. Zero when there is nothing to page through: the live window prints
    /// <c>0 / 0</c> on a fresh install (R334), where an earlier reading with data showed <c>1 / 1</c>.
    /// </summary>
    public int ReleasePages => (_services.Stats.ByStoreInPeriod(CurrentPeriod.From, CurrentPeriod.To).Count + 2) / 3;'''
assert old_pages in t
t = t.replace(old_pages, new_pages, 1)

# 2) the releases empty state, verbatim from the running build
old_rel = '''        _releases.Children.Clear();
        foreach (var card in LoadReleases(byStore).Skip(_releasePage * 3).Take(3))
            _releases.Children.Add(card);'''
new_rel = '''        _releases.Children.Clear();
        var cards = LoadReleases(byStore);
        if (cards.Count == 0)
        {
            // R334: the live empty state, verbatim.
            _releases.Children.Add(new TextBlock { Text = EmptyHeadline, FontWeight = FontWeight.SemiBold });
            _releases.Children.Add(new TextBlock { Text = EmptyReleasesBody, Opacity = 0.6, FontSize = 11 });
        }
        else
        {
            foreach (var card in cards.Skip(_releasePage * 3).Take(3))
                _releases.Children.Add(card);
        }'''
assert old_rel in t
t = t.replace(old_rel, new_rel, 1)

# 3) the constant itself
anchor = '''    /// <summary>The two empty states, verbatim from the window.</summary>'''
add = '''    /// <summary>The releases empty state's second line, verbatim from the running window (R334).</summary>
    public const string EmptyReleasesBody = "There are no upcoming releases";

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Releases: 0/0 pager + empty state added')
