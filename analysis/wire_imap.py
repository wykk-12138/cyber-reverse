import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- ImapView
old_head = '''        var rows = new ListBox { Height = 190 };
        var count = new TextBlock { Opacity = 0.7 };
        var empty = UiKit.Empty("Nothing to see here");

        var aycd = doc.AycdInbox;'''
new_head = '''        // R84: a table, not a list of formatted strings — the live page has three columns.
        var rows = new AccountTable(Columns, "Nothing to see here", EmptySubtitle);
        var count = new TextBlock { Opacity = 0.7 };

        var aycd = doc.AycdInbox;'''
if old_head not in t:
    raise SystemExit("imap head anchor missing")
t = t.replace(old_head, new_head, 1)

old_fill = '''            rows.ItemsSource = doc.Imap
                .Select(a => $"{a.Host}    {a.User}    {a.InboxCount}")
                .ToList();

            count.Text = doc.Imap.Count + (doc.Imap.Count == 1 ? " Account" : " Accounts");

            var any = doc.Imap.Count > 0;
            rows.IsVisible = any;
            empty.IsVisible = !any;
'''
new_fill = '''            rows.Rows = doc.Imap
                .Select(a => new[] { a.Host, a.User, a.InboxCount.ToString() })
                .ToArray();

            count.Text = doc.Imap.Count + (doc.Imap.Count == 1 ? " Account" : " Accounts");
'''
if old_fill not in t:
    raise SystemExit("imap fill anchor missing")
t = t.replace(old_fill, new_fill, 1)

# the class's own constants
old_cls = '''public sealed class ImapView : UserControl
{
    /// <summary>The six Imap Provider presets the live Add Imap Account dialog offers.</summary>'''
new_cls = '''public sealed class ImapView : UserControl
{
    /// <summary>The live page's three columns, read off the running build in R75.</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Host", "Email", "Inbox Count" };

    /// <summary>The empty state's second line, as the live page words it.</summary>
    public const string EmptySubtitle = "Add some accounts to get started";

    /// <summary>The six Imap Provider presets the live Add Imap Account dialog offers.</summary>'''
if old_cls not in t:
    raise SystemExit("imap class anchor missing")
t = t.replace(old_cls, new_cls, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ImapView wired to AccountTable")
