import io
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views'

# 1) BillingView: replace the inline empty block with EmptyView.For("profiles")
p = R + r'\BillingView.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        if (profiles.Count == 0)
        {
            var empty = new StackPanel { Spacing = 4, Margin = new Thickness(0, 60), HorizontalAlignment = HorizontalAlignment.Center };
            empty.Children.Add(new TextBlock { Text = EmptyHeadline, FontWeight = FontWeight.SemiBold, HorizontalAlignment = HorizontalAlignment.Center });
            empty.Children.Add(new TextBlock { Text = EmptyBody, Opacity = 0.6, FontSize = 11, HorizontalAlignment = HorizontalAlignment.Center });
            _rows.Children.Add(empty);
            return;
        }'''
new = '''        if (profiles.Count == 0)
        {
            // R209: one shared EmptyView instead of a hand-built block per page.
            _rows.Children.Add(new EmptyView.For("profiles") { Margin = new Thickness(0, 40) });
            return;
        }'''
assert old in t, 'billing empty block'
t = t.replace(old, new)
# EmptyBody/EmptyHeadline now come from EmptyView; keep the constants but point them at it
t = t.replace('''    /// <summary>The empty state, verbatim.</summary>
    public const string EmptyHeadline = "Nothing to see here";

    /// <inheritdoc cref="EmptyHeadline"/>
    public const string EmptyBody = "Add some profiles to get started";''',
'''    /// <summary>The empty state, from the one place that owns it.</summary>
    public const string EmptyHeadline = EmptyView.Headline;

    /// <inheritdoc cref="EmptyHeadline"/>
    public static string EmptyBody => EmptyView.Bodies["profiles"];''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('billing rewired')

# 2) AnalyticsView (Home): its EmptyBlock() now delegates
p2 = R + r'\Analytics\AnalyticsViews.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''    private static Control EmptyBlock()
    {
        var panel = new StackPanel
        {
            Spacing = 4,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 24),
        };
        panel.Children.Add(new TextBlock
        {
            Text = EmptyHeadline,
            FontWeight = FontWeight.SemiBold,
            HorizontalAlignment = HorizontalAlignment.Center,
        });
        panel.Children.Add(new TextBlock
        {
            Text = EmptyPeriodBody,
            Opacity = 0.6,
            FontSize = 11,
            HorizontalAlignment = HorizontalAlignment.Center,
        });
        return panel;
    }'''
new2 = '''    private static Control EmptyBlock() =>
        // R209: the shared EmptyView owns the glyph, the headline and the second line.
        new Common.EmptyView(EmptyPeriodBody) { Margin = new Thickness(0, 24) };'''
assert old2 in t2, 'analytics empty block'
t2 = t2.replace(old2, new2)
t2 = t2.replace('''    public const string EmptyHeadline = "Nothing to see here";''',
'''    public const string EmptyHeadline = Common.EmptyView.Headline;''')
t2 = t2.replace('''    public const string EmptyPeriodBody = "You haven't made any checkouts for this period";''',
'''    public static string EmptyPeriodBody => Common.EmptyView.Bodies["checkouts"];''')
t2 = t2.replace('''    public const string EmptyFeedBody = "You haven't made any checkouts yet";''',
'''    public static string EmptyFeedBody => Common.EmptyView.Bodies["feed"];''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('analytics rewired')
