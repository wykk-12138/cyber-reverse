import io

add_proxy = '''
    /// <summary>
    /// The header grid and every row grid must reserve the same width for the toolbar column.
    ///
    /// <para>
    /// R72: the last column was <c>Auto</c>. In the header it sized itself to the buttons; in a row
    /// there is nothing in it, so it collapsed — and the four star columns then got different
    /// widths in the two grids. The header said IP/Port/Username/Status at one set of x positions
    /// and the cells landed at another. A screenshot showed it; no assertion did.
    /// </para>
    /// </summary>
    [Fact]
    public void TheHeaderAndTheRowsReserveTheSameToolbarWidth()
    {
        var actions = new StackPanel { Children = { new Button { Content = "Add Proxies" } } };
        var grid = new ProxyGrid(new List<Proxy> { Make("10.0.0.1") }).WithHeaderActions(actions);
        var root = (DockPanel)grid.Content!;

        var header = (Grid)root.Children[0];
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var row = body.Children.OfType<Grid>().First();

        Assert.Equal(header.ColumnDefinitions.Count, row.ColumnDefinitions.Count);

        var headerLast = header.ColumnDefinitions[header.ColumnDefinitions.Count - 1];
        var rowLast = row.ColumnDefinitions[row.ColumnDefinitions.Count - 1];

        _out.WriteLine($"header last = {headerLast.Width}, row last = {rowLast.Width}");

        Assert.True(headerLast.Width.IsAbsolute, "the toolbar column must be a fixed width");
        Assert.Equal(headerLast.Width.Value, rowLast.Width.Value);
    }
}
'''

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ProxiesPageTests.cs"
t = io.open(p, encoding="utf-8").read().rstrip()
assert t.endswith("}")
t = t[:-1].rstrip() + "\n" + add_proxy
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("added proxy alignment test")

add_account = '''
    /// <summary>
    /// Same guard as the proxies table: the header and the rows have to reserve the same width for
    /// the toolbar column, or the columns drift apart.
    /// </summary>
    [Fact]
    public void TheHeaderAndTheRowsReserveTheSameToolbarWidth()
    {
        var actions = new StackPanel { Children = { new Button { Content = "Add Accounts" } } };
        var grid = new AccountGrid(new List<Account> { Make("a@example.com") }).WithHeaderActions(actions);
        var root = (DockPanel)grid.Content!;

        var header = (Grid)root.Children[0];
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var row = body.Children.OfType<Grid>().First();

        Assert.Equal(header.ColumnDefinitions.Count, row.ColumnDefinitions.Count);

        var headerLast = header.ColumnDefinitions[header.ColumnDefinitions.Count - 1];
        var rowLast = row.ColumnDefinitions[row.ColumnDefinitions.Count - 1];

        _out.WriteLine($"header last = {headerLast.Width}, row last = {rowLast.Width}");

        Assert.True(headerLast.Width.IsAbsolute, "the toolbar column must be a fixed width");
        Assert.Equal(headerLast.Width.Value, rowLast.Width.Value);
    }
}
'''

p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\AccountsPageTests.cs"
t2 = io.open(p2, encoding="utf-8").read().rstrip()
assert t2.endswith("}")
t2 = t2[:-1].rstrip() + "\n" + add_account
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("added accounts alignment test")
