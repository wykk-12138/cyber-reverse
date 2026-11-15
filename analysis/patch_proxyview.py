import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("    private readonly IReadOnlyList<ProxyGroup> _groups;",
     "    private readonly IList<ProxyGroup> _groups;"),
    ("    public ProxyView(IReadOnlyList<ProxyGroup> groups, Action? onChanged = null)",
     "    public ProxyView(IList<ProxyGroup> groups, Action? onChanged = null)"),
    ("            _groupsOf(_groups).Add(group);",
     "            _groups.Add(group);"),
    ("p.Status.IsRunning",
     'string.Equals(p.Status.Text, "Running", StringComparison.Ordinal)'),
    ('moreItems.Add(MenuItem("Test All"',
     'moreItems.Add(MoreItem("Test All"'),
    ('moreItems.Add(MenuItem("Clear Failed"',
     'moreItems.Add(MoreItem("Clear Failed"'),
    ("moreItems.Add(MenuItem(ProxyGrid.ClearOverCaption",
     "moreItems.Add(MoreItem(ProxyGrid.ClearOverCaption"),
    ("    private static MenuItem MenuItem(string header, Action action)",
     "    private static MenuItem MoreItem(string header, Action action)"),
]

for old, new in subs:
    if old not in t:
        raise SystemExit("MISS: " + old[:70])
    t = t.replace(old, new, 1)

# Drop the now-unused helper block.
start = t.find("    /// <summary>A group list the page can add to.")
if start >= 0:
    end = t.find("    private Control BuildDetail()", start)
    t = t[:start] + t[end:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
