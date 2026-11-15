import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\UiKit.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    public static ScrollViewer Scroll(Control content) => new()"
helper = '''    /// <summary>
    /// A page header: the large title over its one-line subtitle, as every Settings page prints it
    /// in the original (gear, title, subtitle, divider).
    ///
    /// <para>
    /// R74 read four of these off the live build — General, Data, Webhooks and Captcha Providers.
    /// They are per page, not per nav entry: the rail says "Captcha Providers" while the page
    /// itself is titled "3rd Party Captcha Providers".
    /// </para>
    /// </summary>
    public static Control PageHeader(string title, string subtitle) => new StackPanel
    {
        Spacing = 2,
        Margin = new Thickness(0, 0, 0, 10),
        Children =
        {
            new TextBlock { Text = title, FontSize = 20, FontWeight = FontWeight.SemiBold },
            new TextBlock { Text = subtitle, Opacity = 0.6, FontSize = 12 },
        },
    };

'''

if anchor not in t:
    raise SystemExit("UiKit anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, helper + anchor, 1))
print("PageHeader added")
