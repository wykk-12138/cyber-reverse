import io
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views'

# TaskGrid
p = R + r'\Tasks\TaskGrid.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        if (_rows.Count == 0)
        {
            body.Children.Add(new StackPanel
            {
                Spacing = 4,
                Margin = new Thickness(0, 60, 0, 0),
                HorizontalAlignment = HorizontalAlignment.Center,
                Children =
                {
                    new TextBlock
                    {
                        Text = "Nothing to see here",
                        FontSize = 18,
                        FontWeight = FontWeight.SemiBold,
                        HorizontalAlignment = HorizontalAlignment.Center,
                    },
                    new TextBlock
                    {
                        Text = "Add some tasks to get started",
                        Opacity = 0.6,
                        HorizontalAlignment = HorizontalAlignment.Center,
                    },
                },
            });
        }'''
new = '''        if (_rows.Count == 0)
        {
            // R209: the shared EmptyView owns the glyph, the headline and this page's second line.
            body.Children.Add(EmptyView.For("tasks") is var block ? WithTopMargin(block) : block);
        }'''
assert old in t, 'taskgrid block'
t = t.replace(old, new)
# helper
t = t.replace('''    private static Control Docked(Control control, Dock dock)''',
'''    /// <summary>Keeps the measured 60 px gap above the empty state.</summary>
    private static Control WithTopMargin(Control control)
    {
        control.Margin = new Thickness(0, 60, 0, 0);
        return control;
    }

    private static Control Docked(Control control, Dock dock)''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('taskgrid rewired')

# ProxyGrid
p2 = R + r'\Proxies\ProxyGrid.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''            var empty = new StackPanel
            {
                Spacing = 4,
                Margin = new Thickness(0, 60, 0, 0),
                HorizontalAlignment = HorizontalAlignment.Center,
                Children =
                {
                    // Empty.Nothing.Title
                    new TextBlock
                    {
                        Text = "Nothing to see here",
                        FontSize = 18,
                        FontWeight = FontWeight.SemiBold,
                        HorizontalAlignment = HorizontalAlignment.Center,
                    },
                    // Proxies.Empty.Subtitle
                    new TextBlock
                    {
                        Text = "Add some proxies to get started",
                        Opacity = 0.6,
                        HorizontalAlignment = HorizontalAlignment.Center,
                    },
                },
            };
            body.Children.Add(empty);'''
new2 = '''            // R209: Empty.Nothing.Title + Proxies.Empty.Subtitle now live in the shared EmptyView.
            var empty = EmptyView.For("proxies");
            empty.Margin = new Thickness(0, 60, 0, 0);
            body.Children.Add(empty);'''
assert old2 in t2, 'proxygrid block'
t2 = t2.replace(old2, new2)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('proxygrid rewired')
