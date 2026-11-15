import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- GoogleAccountsView
old_cls = '''public sealed class GoogleAccountsView : UserControl
{'''
new_cls = '''public sealed class GoogleAccountsView : UserControl
{
    /// <summary>The live page's two columns (locale: Settings.Google.Header.Name / .Email).</summary>
    public static readonly IReadOnlyList<string> Columns = new[] { "Name", "Email" };

    /// <summary>The empty state's second line, as the live page words it.</summary>
    public const string EmptySubtitle = "Add some Google accounts to get started";
'''
if old_cls not in t:
    raise SystemExit("google class anchor missing")
t = t.replace(old_cls, new_cls, 1)

old_head = '''        var rows = new ListBox { Height = 190 };'''
# this appears twice (Google, and maybe elsewhere) — scope to the Google class body
gstart = t.find("public sealed class GoogleAccountsView")
ghead = t.find("var rows = new ListBox { Height = 190 };", gstart)
if ghead < 0:
    raise SystemExit("google listbox not found")
t = t[:ghead] + '        // R84: two columns, as the live page shows (Settings.Google.Header.*).\n' \
                '        var rows = new AccountTable(Columns, "Nothing to see here", EmptySubtitle);' \
                + t[ghead + len(old_head):]

old_fill = '''            rows.ItemsSource = doc.Google'''
i = t.find(old_fill, gstart)
if i < 0:
    raise SystemExit("google fill not found")
# find the end of the assignment statement
end = t.find(";", i)
# extend across a multi-line expression: take to the first ";" followed by newline
j = t.find("\n", t.find("ToList()", i)) if "ToList()" in t[i:i + 400] else end
t = t[:i] + "            rows.Rows = doc.Google\n                .Select(a => new[] { a.Name ?? a.Email, a.Email })\n                .ToArray()" + t[j:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("GoogleAccountsView wired (fill expression needs review)")
