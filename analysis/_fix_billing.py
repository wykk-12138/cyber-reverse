import io
R = r'D:\projects\cyber-reverse\replica'

# (a) re-entrancy guard in BillingView.Refresh
p = R + r'\src\Cybersole.Ui\Views\BillingView.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''    private BillingGroup? _selected;''',
'''    private BillingGroup? _selected;
    // Refresh() reassigns _groups.ItemsSource, which raises SelectionChanged and re-enters Refresh. Avalonia answers
    // "Cannot change source while update is in progress" (measured), so the handler is gated.
    private bool _refreshing;''')
t = t.replace('''        _groups.SelectionChanged += (_, _) =>
        {
            _selected = _groups.SelectedItem as BillingGroup;
            Refresh();
        };''',
'''        _groups.SelectionChanged += (_, _) =>
        {
            if (_refreshing) return;
            _selected = _groups.SelectedItem as BillingGroup;
            Refresh();
        };''')
t = t.replace('''    public void Refresh()
    {
        var groupFilter''',
'''    public void Refresh()
    {
        if (_refreshing) return;
        _refreshing = true;
        try
        {
        var groupFilter''')
t = t.replace('''            _rows.Children.Add(row);
        }
    }''',
'''            _rows.Children.Add(row);
        }
        }
        finally { _refreshing = false; }
    }''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('guard added')

# (b) CloneNamingTests: BillingView no longer clones
p2 = R + r'\tests\Cybersole.Tests\CloneNamingTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''    public static TheoryData<string> ProfileCloneSites => new()
    {
        "src/Cybersole.Ui/Views/BillingView.cs",
        "src/Cybersole.Ui/Views/Profiles/ProfileViews.cs",
    };''',
'''    public static TheoryData<string> ProfileCloneSites => new()
    {
        // R208: BillingView dropped its clone action. The running 5.18.32 build draws that page with exactly two
        // buttons — "Add Profile" and "Clear Profiles" — so a clone helper there was a replica invention, and a
        // test that demanded a rename in it was protecting the invention rather than the target.
        "src/Cybersole.Ui/Views/Profiles/ProfileViews.cs",
    };''')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('clone test updated')
