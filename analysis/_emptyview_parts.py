import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\EmptyView.cs'
t = io.open(p, encoding='utf-8').read()

t = t.replace('''    public EmptyView(string body, double iconSize = 96)
    {''',
'''    /// <summary>The headline element, so a test can read what is on screen without guessing the tree shape.</summary>
    public TextBlock HeadlineText { get; }

    /// <summary>The page-specific second line.</summary>
    public TextBlock BodyText { get; }

    /// <summary>The circular glyph the window draws above the headline.</summary>
    public Border Icon { get; }

    public EmptyView(string body, double iconSize = 96)
    {''')

t = t.replace('''        panel.Children.Add(new Border
        {''', '''        var icon = new Border
        {''')
t = t.replace('''        });

        panel.Children.Add(new TextBlock
        {
            Text = Headline,
            FontWeight = FontWeight.SemiBold,''', '''        };
        Icon = icon;
        panel.Children.Add(icon);

        var headline = new TextBlock
        {
            Text = Headline,
            FontWeight = FontWeight.SemiBold,''')
t = t.replace('''            Margin = new Thickness(0, 10, 0, 0),
        });

        panel.Children.Add(new TextBlock
        {
            Text = body,
            Opacity = 0.6,
            FontSize = 12,
            HorizontalAlignment = HorizontalAlignment.Center,
        });''', '''            Margin = new Thickness(0, 10, 0, 0),
        };
        HeadlineText = headline;
        panel.Children.Add(headline);

        var bodyText = new TextBlock
        {
            Text = body,
            Opacity = 0.6,
            FontSize = 12,
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        BodyText = bodyText;
        panel.Children.Add(bodyText);''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('EmptyView exposes its parts')
