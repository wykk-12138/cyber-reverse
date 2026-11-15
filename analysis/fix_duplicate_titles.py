import io

# 1) A card without a title, for the case where the page header already says it.
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\UiKit.cs"
t = io.open(p, encoding="utf-8").read()
anchor = "    public static ScrollViewer Scroll(Control content) => new()"
helper = '''    /// <summary>
    /// A bordered card with no title, for a page whose header already carries the name.
    ///
    /// <para>
    /// R75: five Settings pages printed their own name twice — once in the page header and once in
    /// the card right below it ("Custom Stores" over "Custom Stores"). The header is the title; the
    /// card does not need to repeat it.
    /// </para>
    /// </summary>
    public static Border PlainCard(params Control[] children)
    {
        var stack = new StackPanel { Spacing = 8 };
        foreach (var child in children) stack.Children.Add(child);

        return new Border
        {
            BorderThickness = new Thickness(1),
            BorderBrush = new SolidColorBrush(Color.Parse("#2A2E3A")),
            CornerRadius = new CornerRadius(8),
            Padding = new Thickness(12),
            Margin = new Thickness(0, 0, 0, 8),
            Child = stack,
        };
    }

'''
if anchor not in t:
    raise SystemExit("UiKit anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, helper + anchor, 1))
print("PlainCard added")

# 2) The five pages whose section title repeats their page header.
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t2 = io.open(p2, encoding="utf-8").read()
for title in ('"3rd Party Cloudflare Providers",', '"Custom Sizes",', '"Custom Stores",', '"Data",', '"Webhooks",'):
    old = 'UiKit.Section(%s' % title
    new = 'UiKit.PlainCard('
    if old not in t2:
        raise SystemExit("section anchor missing: " + title)
    t2 = t2.replace(old, new, 1)
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("five duplicate card titles removed")
