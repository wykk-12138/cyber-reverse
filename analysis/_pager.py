import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()

old = '''        _pageLabel.Text = ReleasePage + " / " + ReleasePages;'''
new = '''        _pageLabel.Text = PagerCaption(ReleasePage, ReleasePages);'''
assert old in t
t = t.replace(old, new, 1)

anchor = '''    /// <summary>The releases empty state's second line, verbatim from the running window (R334).</summary>'''
add = '''    /// <summary>
    /// How the carousel pager reads. With nothing to page through the live window prints <c>0 / 0</c> (R334), not
    /// <c>1 / 1</c> — the page counter follows the number of pages, it does not default to one.
    /// </summary>
    public static string PagerCaption(int page, int pages) => pages <= 0 ? "0 / 0" : $"{page} / {pages}";

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('PagerCaption added')
