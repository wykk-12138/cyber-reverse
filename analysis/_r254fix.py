import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''    /// <summary>How many charts the page can show (the segment names).</summary>
    public IReadOnlyList<string> Charts => Segments;

''', '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('duplicate Charts removed (it already existed)')
