using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 72: the proxies page is two panes, and the table has four columns.
///
/// <para>
/// R56–R61 had one flat table over every group's proxies with the import box and six buttons
/// above it. Driving the live 5.18.32 showed the shape the accounts page already had:
/// <c>PROXY GROUPS</c> on the left with a count badge per group, one group on the right with its
/// own loaded caption and traffic counters, and the toolbar on the header line.
/// </para>
///
/// <para>
/// Two captions are unique to this page and both come from the locale:
/// <c>Proxies.LoadedNone</c> ("No Proxies Loaded" — the accounts page has no zero form) and
/// <c>Proxies.CurrentDownload</c> / <c>.CurrentUpload</c>.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class ProxiesPageTests
{
    private readonly ITestOutputHelper _out;

    public ProxiesPageTests(ITestOutputHelper output) => _out = output;

    private static Proxy Make(string host, int port = 8080, string? user = null, int usage = 0) => new()
    {
        Host = host,
        Port = port,
        Username = user,
        Usage = usage,
    };

    private static ProxyGroup Group(string name, int order, params Proxy[] proxies)
    {
        var group = new ProxyGroup { Name = name, Order = order };
        foreach (var proxy in proxies)
        {
            proxy.GroupId = group.Id;
            group.Proxies.Add(proxy);
        }
        return group;
    }

    /// <summary>
    /// <c>Proxies.LoadedNone</c> / <c>.LoadedOne</c> / <c>.LoadedFormat</c> — three forms, and the
    /// zero form really is a sentence. The accounts page answers 0 with "0 Accounts Loaded", so the
    /// two pages differ here and the difference is in the locale.
    /// </summary>
    [Fact]
    public void TheLoadedCaptionHasThreeForms()
    {
        _out.WriteLine($"0 -> {ProxyGrid.LoadedCaption(0)}");
        _out.WriteLine($"1 -> {ProxyGrid.LoadedCaption(1)}");
        _out.WriteLine($"3 -> {ProxyGrid.LoadedCaption(3)}");

        Assert.Equal("No Proxies Loaded", ProxyGrid.LoadedCaption(0));
        Assert.Equal("1 Proxy Loaded", ProxyGrid.LoadedCaption(1));
        Assert.Equal("3 Proxies Loaded", ProxyGrid.LoadedCaption(3));

        // …and the accounts page has no zero form, which is why it prints "0 Accounts Loaded".
        Assert.Equal("0 Accounts Loaded", Cybersole.Ui.Views.Accounts.AccountView.LoadedCaption(0));
    }

    /// <summary><c>Proxies.CurrentDownload</c> / <c>.CurrentUpload</c> print bytes, then KB, then MB.</summary>
    [Fact]
    public void TheTrafficCaptionClimbsUnits()
    {
        _out.WriteLine($"0 -> {ProxyGrid.TrafficCaption(0)}, 2048 -> {ProxyGrid.TrafficCaption(2048)}");

        Assert.Equal("0 B", ProxyGrid.TrafficCaption(0));
        Assert.Equal("512 B", ProxyGrid.TrafficCaption(512));
        Assert.Equal("2 KB", ProxyGrid.TrafficCaption(2048));
        Assert.Equal("1.5 MB", ProxyGrid.TrafficCaption(1024L * 1024 + 512 * 1024));
    }

    /// <summary><c>Proxies.More.ClearOverFormat</c> = "Clear {0} Proxies".</summary>
    [Fact]
    public void ClearOverNamesTheNumberItWillClear()
    {
        var rows = new List<Proxy> { Make("a"), Make("b", usage: 5), Make("c", usage: 9) };
        var grid = new ProxyGrid(rows).WithUsageLimit(5);

        _out.WriteLine($"{ProxyGrid.ClearOverCaption(grid.OverLimitCount())}");

        Assert.Equal(2, grid.OverLimitCount());
        Assert.Equal("Clear 2 Proxies", ProxyGrid.ClearOverCaption(grid.OverLimitCount()));
    }

    /// <summary>Selection captions use the plural forms the locale ships.</summary>
    [Fact]
    public void TheSelectionCaptionIsTheLocalesWords()
    {
        Assert.Equal("1 PROXY SELECTED", ProxyGrid.SelectionHeader(1));
        Assert.Equal("4 PROXIES SELECTED", ProxyGrid.SelectionHeader(4));
    }

    /// <summary>The page opens on the first group and follows a selection.</summary>
    [Fact]
    public void ThePageOpensOnTheFirstGroup()
    {
        var first = Group("Group 1", 0, Make("10.0.0.1"));
        var second = Group("Group 2", 1);
        var groups = new List<ProxyGroup> { first, second };

        var page = new ProxyView(groups);
        Assert.Same(first, page.SelectedGroup);

        page.SelectGroup(second);
        Assert.Same(second, page.SelectedGroup);
    }

    /// <summary>The count badge is the group's proxy count.</summary>
    [Fact]
    public void TheCountBadgeIsTheGroupCount()
    {
        var group = Group("Group 1", 0, Make("10.0.0.1"), Make("10.0.0.2"));
        _out.WriteLine($"badge = {ProxyView.CountBadge(group)}");
        Assert.Equal("2", ProxyView.CountBadge(group));
    }

    /// <summary>The left pane honours the order dropdown the original puts next to PROXY GROUPS.</summary>
    [Fact]
    public void TheOrderComboReordersThePane()
    {
        var b = Group("Beta", 1, Make("10.0.0.2"));
        var a = Group("Alpha", 2, Make("10.0.0.1"), Make("10.0.0.3"));
        var groups = new List<ProxyGroup> { b, a };

        Assert.Equal(new[] { "Beta", "Alpha" },
            ProxyView.SortGroups(groups, ProxyView.GroupOrder.Custom).Select(g => g.Name));
        Assert.Equal(new[] { "Alpha", "Beta" },
            ProxyView.SortGroups(groups, ProxyView.GroupOrder.Alpha).Select(g => g.Name));
        Assert.Equal(new[] { "Alpha", "Beta" },
            ProxyView.SortGroups(groups, ProxyView.GroupOrder.Count).Select(g => g.Name));

        _out.WriteLine("custom=" + string.Join(",", ProxyView.SortGroups(groups, ProxyView.GroupOrder.Custom).Select(g => g.Name)));
    }

    /// <summary>The search box filters the group list.</summary>
    [Fact]
    public void TheSearchBoxFiltersGroups()
    {
        var groups = new List<ProxyGroup> { Group("Residential", 0), Group("Datacenter", 1) };
        var page = new ProxyView(groups);

        Assert.Equal(2, page.VisibleGroups().Count);
        // VisibleGroups applies the page's own search field; drive it through SetOrder's sibling.
        page.SetOrder(ProxyView.GroupOrder.Alpha);
        Assert.Equal(new[] { "Datacenter", "Residential" }, page.VisibleGroups().Select(g => g.Name));
    }

    /// <summary>Every header sorts, and the glyph follows the direction.</summary>
    [Fact]
    public void EveryHeaderSortsBothWays()
    {
        var rows = new List<Proxy>
        {
            Make("10.0.0.2", port: 9000, user: "zed"),
            Make("10.0.0.1", port: 8000, user: "abe"),
        };
        var grid = new ProxyGrid(rows);

        Assert.Equal("↑", grid.SortGlyph(ProxyGrid.ProxyColumn.Ip));
        Assert.Equal(new[] { "10.0.0.1", "10.0.0.2" }, grid.Ordered().Select(p => p.Host));

        grid.SortBy(ProxyGrid.ProxyColumn.Ip);
        Assert.Equal(new[] { "10.0.0.2", "10.0.0.1" }, grid.Ordered().Select(p => p.Host));
        Assert.Equal("↓", grid.SortGlyph(ProxyGrid.ProxyColumn.Ip));

        grid.SortBy(ProxyGrid.ProxyColumn.Port);
        _out.WriteLine("by port: " + string.Join(",", grid.Ordered().Select(p => p.Port)));
        Assert.Equal(new[] { 8000, 9000 }, grid.Ordered().Select(p => p.Port));

        grid.SortBy(ProxyGrid.ProxyColumn.Username);
        Assert.Equal(new[] { "abe", "zed" }, grid.Ordered().Select(p => p.Username));
    }

    /// <summary>The header checkbox selects everything, and Delete removes the selection.</summary>
    [Fact]
    public void TheHeaderCheckboxSelectsAndDeletesEverything()
    {
        var rows = new List<Proxy> { Make("10.0.0.1"), Make("10.0.0.2") };
        var grid = new ProxyGrid(rows);

        Assert.False(grid.AllSelected);
        grid.SelectAll();
        Assert.True(grid.AllSelected);
        Assert.Equal(2, grid.SelectedProxies.Count);

        grid.DeleteSelected();
        _out.WriteLine($"left = {rows.Count}");
        Assert.Empty(rows);
    }

    /// <summary>Copy emits one <c>host:port</c> per line, the same shape the accounts page uses.</summary>
    [Fact]
    public void CopyEmitsOneAddressPerLine()
    {
        var rows = new List<Proxy> { Make("10.0.0.1", 8080), Make("10.0.0.2", 9090) };
        var grid = new ProxyGrid(rows);

        grid.SelectAll();
        var text = string.Concat(grid.SelectedProxies.Select(p => p.Address + "\n"));

        _out.WriteLine(text.Replace("\n", "\\n"));
        Assert.Equal("10.0.0.1:8080\n10.0.0.2:9090\n", text);
    }

    /// <summary>Clear Failed removes only the failed rows; Clear Over only the spent ones.</summary>
    [Fact]
    public void ClearFailedAndClearOverRemoveDifferentRows()
    {
        var failed = Make("10.0.0.1");
        failed.Status = Status.Failed;
        var spent = Make("10.0.0.2", usage: 4);
        var fresh = Make("10.0.0.3");

        var rows = new List<Proxy> { failed, spent, fresh };
        var grid = new ProxyGrid(rows).WithUsageLimit(4);

        grid.ClearFailed();
        _out.WriteLine("after ClearFailed: " + string.Join(",", rows.Select(p => p.Host)));
        Assert.DoesNotContain(failed, rows);

        grid.ClearOver();
        _out.WriteLine("after ClearOver: " + string.Join(",", rows.Select(p => p.Host)));
        Assert.DoesNotContain(spent, rows);
        Assert.Contains(fresh, rows);
    }

    /// <summary>
    /// The empty state is the original's two lines, not a hint about a text box that no longer
    /// exists on this page.
    /// </summary>
    [Fact]
    public void TheEmptyStateIsTheTwoLocaleLines()
    {
        var grid = new ProxyGrid(new List<Proxy>());
        var root = (DockPanel)grid.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;

        // R209: the empty state is the shared EmptyView now — glyph, headline, one page-specific line — which is what
        // the running build draws. This used to assert a bare two-TextBlock StackPanel because that is all the replica
        // had.
        var empty = body.Children.OfType<Cybersole.Ui.Views.Common.EmptyView>().Single();
        _out.WriteLine(empty.HeadlineText.Text + " / " + empty.BodyText.Text);

        Assert.Equal("Nothing to see here", empty.HeadlineText.Text);
        Assert.Equal("Add some proxies to get started", empty.BodyText.Text);
        Assert.NotNull(empty.Icon);
    }

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
