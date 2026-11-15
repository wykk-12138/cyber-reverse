import io, os, re

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests"

# 1) Menu labels changed to the locale's wording in R72.
renames = [
    ('"Move To…"', '"Move proxies to"'),
    ('"Test On"', '"Test Proxies"'),
]
for name in ["ProxyCloneMoveTests.cs", "ProxyRowTestTests.cs"]:
    p = os.path.join(base, name)
    t = io.open(p, encoding="utf-8").read()
    before = t
    for old, new in renames:
        t = t.replace(old, new)
    if t != before:
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("renamed labels in", name)

# 2) The toolbar moved onto the header row, and there are four columns, not five.
p = os.path.join(base, "RenderedProxyTableTests.cs")
t = io.open(p, encoding="utf-8").read()

start = t.find("    /// <summary>\n    /// The toolbar sits above the column headers.")
if start < 0:
    raise SystemExit("toolbar test not found")
end = t.find("    /// <summary>\n    /// A group with no UsageExpiry", start)
assert end > start

replacement = '''    /// <summary>
    /// The toolbar shares the header row, and the table has the four columns the locale names.
    ///
    /// <para>
    /// R72: this test used to assert the opposite — a toolbar as its own row above five column
    /// headers, the fifth being <c>Usage</c>. Driving the live 5.18.28 showed one header line
    /// carrying <c>[☐] IP⇅ Port⇅ Username⇅ Status⇅</c> and the three buttons on the same line, and
    /// <c>Proxies.Column.*</c> has exactly four keys. Usage is still what Clear Over compares
    /// against; it is simply not a column.
    /// </para>
    /// </summary>
    [Fact]
    public void TheToolbarSharesTheHeaderRow()
    {
        var actions = new StackPanel { Children = { new Button { Content = "Add Proxies" } } };
        var view = new ProxyGrid(new List<Proxy> { Make("10.0.0.1") }).WithHeaderActions(actions);
        var root = (DockPanel)view.Content!;

        // children: [header, scroll] — the toolbar is a child of the header, not a row of its own.
        Assert.Equal(2, root.Children.Count);

        var header = (Grid)root.Children[0];
        _out.WriteLine($"header children = {header.Children.Count}");

        Assert.Contains(actions, header.Children);

        var labels = header.Children.OfType<Button>()
            .Select(b => (b.Content as TextBlock)?.Text ?? string.Empty).ToList();

        _out.WriteLine("header: " + string.Join(",", labels));

        // The first column is the one the table is already sorted by, so it carries the glyph.
        Assert.Equal(new[] { "IP ↑", "Port", "Username", "Status" }, labels);
    }

'''

t = t[:start] + replacement + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("rewrote the toolbar test")
