using System.Collections.Generic;
using System.Linq;
using Cybersole.Ui.Views.Common;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R210: <c>GroupGrid</c> — the left rail row that Proxies, Accounts and Billing all draw. Proxies uses it now; the
/// other two still build their own row, which is recorded here rather than pretended away.
/// </summary>
public sealed class GroupGridTests
{
    private readonly ITestOutputHelper _out;
    public GroupGridTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void RowsShowTheNameAndTheBadge()
    {
        var grid = new GroupGrid();
        grid.SetRows(new (string, string, string)[]
        {
            ("g1", "Group 1", "0"),
            ("g2", "Group 2", "12"),
        }, "g1", null);

        _out.WriteLine(string.Join(" | ", grid.Rows.Select(r => r.Name + "=" + r.Badge)));
        Assert.Equal(2, grid.Rows.Count);
        Assert.Equal(("Group 1", "0"), grid.Rows[0]);
        Assert.Equal(("Group 2", "12"), grid.Rows[1]);
    }

    [Fact]
    public void AnEmptyFilterResultSaysSoInTheWindowsWords()
    {
        Assert.Equal("No groups matched your search", GroupGrid.NoMatch);

        var grid = new GroupGrid();
        grid.SetRows(System.Array.Empty<(string, string, string)>(), null, null);

        Assert.Empty(grid.Rows);
        var panel = (Avalonia.Controls.StackPanel)grid.Content!;
        var text = Assert.IsType<Avalonia.Controls.TextBlock>(panel.Children.Single());
        Assert.Equal(GroupGrid.NoMatch, text.Text);
    }

    [Fact]
    public void TheSelectionCallbackCarriesTheKeyNotTheIndex()
    {
        string? picked = null;
        var grid = new GroupGrid();
        grid.SetRows(new (string, string, string)[] { ("a", "Alpha", "1"), ("b", "Beta", "2") }, null,
            key => picked = key);

        var panel = (Avalonia.Controls.StackPanel)grid.Content!;
        var second = (Avalonia.Controls.Button)panel.Children[1];
        second.RaiseEvent(new Avalonia.Interactivity.RoutedEventArgs(Avalonia.Controls.Button.ClickEvent));

        Assert.Equal("b", picked);
    }

    [Fact]
    public void TheProxyRailIsTheSharedGridAndTheOldOneIsGone()
    {
        var path = System.IO.Path.Combine(Repo(), "src", "Cybersole.Ui", "Views", "Proxies", "ProxyView.cs");
        var source = System.IO.File.ReadAllText(path);

        Assert.Contains("new GroupGrid()", source);
        Assert.Contains("grid.SetRows(", source);

        // the hand-built row is gone: one copy of the badge/selection logic, not two. Comments may still describe the
        // rail (that is documentation), so the check runs on code with the comment lines removed.
        var code = string.Join("\n", System.IO.File.ReadAllLines(path)
            .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

        Assert.DoesNotContain("LegacyLeftPane", code);
        Assert.DoesNotContain("\"No groups matched your search\"", code);
    }

    private static string Repo()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void BillingUsesTheSharedRail()
    {
        var path = System.IO.Path.Combine(Repo(), "src", "Cybersole.Ui", "Views", "BillingView.cs");
        var code = string.Join("\n", System.IO.File.ReadAllLines(path)
            .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

        Assert.Contains("Common.GroupGrid _groups", code);
        Assert.Contains("_groups.SetRows(", code);

        // the ListBox-based rail and its re-entrancy guard are gone with it
        Assert.DoesNotContain("_groups.ItemsSource", code);
        Assert.DoesNotContain("_refreshing", code);
    }

    [Fact]
    public void TheAccountsRailIsATwoLevelTreeSoItDoesNotUseTheGrid()
    {
        // R211, recorded deliberately: the Accounts rail prints a bold platform header and then indented group rows
        // under it, which is not the flat "name + badge" row GroupGrid draws. Forcing the grid there would have made
        // the file look more "1:1" while making the page less like the window.
        var path = System.IO.Path.Combine(Repo(), "src", "Cybersole.Ui", "Views", "Accounts", "AccountView.cs");
        var code = string.Join("\n", System.IO.File.ReadAllLines(path)
            .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

        Assert.Contains("VisiblePlatforms()", code);
        Assert.Contains("GroupsFor(platform)", code);
        Assert.DoesNotContain("GroupGrid", code);
        Assert.Contains("\"No stores matched your search\"", code);
    }
}
