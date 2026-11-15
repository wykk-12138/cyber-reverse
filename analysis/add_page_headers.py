import io

# 1) UiKit.Page — header + body, so the shell can wrap any section.
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\UiKit.cs"
t = io.open(p, encoding="utf-8").read()
anchor = "    public static ScrollViewer Scroll(Control content) => new()"
page = '''    /// <summary>A page: its header over its body.</summary>
    public static Control Page(string title, string subtitle, Control content) => new StackPanel
    {
        Spacing = 6,
        Children = { PageHeader(title, subtitle), content },
    };

'''
if anchor not in t:
    raise SystemExit("UiKit anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, page + anchor, 1))
print("UiKit.Page added")

# 2) SettingsShell: the page header is shell chrome, exactly as it is in the original.
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"
t2 = io.open(p2, encoding="utf-8").read()

table = '''    /// <summary>
    /// The header each page prints, read off the live 5.18.30 build in R74. Only the four pages that
    /// were walked have one; the rest fall back to their nav label with no subtitle, which is what
    /// an unvisited page honestly is.
    ///
    /// <para>
    /// The rail and the page disagree on purpose in one place: the rail says "Captcha Providers"
    /// and the page is titled "3rd Party Captcha Providers".
    /// </para>
    /// </summary>
    public static readonly IReadOnlyDictionary<string, (string Title, string Subtitle)> PageHeaders =
        new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase)
        {
            ["general"] = ("General", "Profile, delays, and other general preferences"),
            ["data"] = ("Data", "Import, export and backup data"),
            ["webhooks"] = ("Webhooks", "Receive real time notifications into your favorite services"),
            ["captcha-providers"] = ("3rd Party Captcha Providers",
                                     "Add and configure 3rd party captcha solving services"),
        };

    /// <summary>The header a section prints: its own if it was walked, else its nav label.</summary>
    public static (string Title, string? Subtitle) PageHeaderFor(string id)
    {
        if (PageHeaders.TryGetValue(id, out var header)) return (header.Title, header.Subtitle);
        var section = Sections.FirstOrDefault(s => string.Equals(s.Id, id, StringComparison.OrdinalIgnoreCase));
        return (section?.Title ?? id, null);
    }

'''
anchor2 = "    /// <summary>Switch to a section by id. Unknown ids are ignored.</summary>"
if anchor2 not in t2:
    raise SystemExit("shell anchor missing")
t2 = t2.replace(anchor2, table + anchor2, 1)

old_host = "        _host.Content = section.Build(_services);"
new_host = '''        var view = section.Build(_services);
        var header = PageHeaderFor(section.Id);
        _host.Content = header.Subtitle is null
            ? view
            : UiKit.Page(header.Title, header.Subtitle, view);'''
if old_host not in t2:
    raise SystemExit("host anchor missing")
t2 = t2.replace(old_host, new_host, 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("SettingsShell wraps sections with their page header")
