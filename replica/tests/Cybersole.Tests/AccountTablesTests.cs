using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 84/85: the three account pages are tables with the live columns, and the columns sort.
///
/// <para>
/// R75 read all three off the running build, and the binary's locale carries the same header sets
/// (<c>Settings.Google.Header.Name/.Email</c>, <c>Settings.PayPal.Header.Email/.Status</c>):
/// </para>
///
/// <code>
/// Email Accounts    Host      Email      Inbox Count     "Add some accounts to get started"
/// Google Accounts   Name      Email                      "Add some Google accounts to get started"
/// PayPal Accounts   Email     Status                     "Add some PayPal accounts to get started"
/// </code>
///
/// <para>
/// All three pages had a <see cref="ListBox"/> of formatted strings — one column's worth of text
/// pretending to be a table, and a one-line empty state. <see cref="AccountTable"/> is the shared
/// shape now, and R85 made its header glyphs honest: they sort.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class AccountTablesTests
{
    private readonly ITestOutputHelper _out;

    public AccountTablesTests(ITestOutputHelper output) => _out = output;

    /// <summary>The columns, page by page, in the live order.</summary>
    [Fact]
    public void TheThreePagesHaveTheLiveColumns()
    {
        _out.WriteLine("email:  " + string.Join(" | ", ImapView.Columns));
        _out.WriteLine("google: " + string.Join(" | ", GoogleAccountsView.Columns));
        _out.WriteLine("paypal: " + string.Join(" | ", PayPalAccountsView.Columns));

        Assert.Equal(new[] { "Host", "Email", "Inbox Count" }, ImapView.Columns);
        Assert.Equal(new[] { "Name", "Email" }, GoogleAccountsView.Columns);
        Assert.Equal(new[] { "Email", "Status" }, PayPalAccountsView.Columns);
    }

    /// <summary>The three empty-state second lines, word for word.</summary>
    [Fact]
    public void TheEmptySubtitleIsTheLiveWording()
    {
        Assert.Equal("Add some accounts to get started", ImapView.EmptySubtitle);
        Assert.Equal("Add some Google accounts to get started", GoogleAccountsView.EmptySubtitle);
        Assert.Equal("Add some PayPal accounts to get started", PayPalAccountsView.EmptySubtitle);
    }

    /// <summary>A table renders a header row and one row per record, and hides the empty pane.</summary>
    [Fact]
    public void TheTableRendersHeaderAndRows()
    {
        var table = new AccountTable(new[] { "Host", "Email", "Inbox Count" },
            "Nothing to see here", "Add some accounts to get started");

        Assert.Contains("Host ⇅", Headers(table));
        Assert.Contains("Nothing to see here", Texts(table));

        table.Rows = new[]
        {
            new[] { "imap.gmail.com", "a@example.com", "12" },
            new[] { "imap.qq.com", "b@example.com", "3" },
        };

        var texts = Texts(table);
        _out.WriteLine("rows: " + string.Join(" / ", texts.Where(t => t.Contains('@'))));

        Assert.Contains("imap.gmail.com", texts);
        Assert.Contains("a@example.com", texts);
        Assert.Contains("12", texts);
        Assert.Contains("b@example.com", texts);

        // the empty pane is hidden once there is a row
        var emptyLine = Descendants(table).OfType<TextBlock>()
            .First(t => t.Text == "Nothing to see here");
        Assert.True(HiddenByAncestor(emptyLine));

        // and the header stays visible
        var header = Descendants(table).OfType<Button>()
            .First(b => (b.Content?.ToString() ?? "").StartsWith("Host", StringComparison.Ordinal));
        _out.WriteLine($"header visible with rows: {header.IsVisible}");
        Assert.True(header.IsVisible);
    }

    /// <summary>An empty row set brings the empty pane back and hides the header.</summary>
    [Fact]
    public void AnEmptyTableShowsTheEmptyPaneAndHidesTheHeader()
    {
        var table = new AccountTable(new[] { "Email", "Status" },
            "Nothing to see here", "Add some PayPal accounts to get started");

        table.Rows = new[] { new[] { "a@example.com", "Active" } };
        table.Rows = Array.Empty<string[]>();

        // IsVisible sits on the header Grid, not on the button inside it — ask the ancestors.
        var header = Descendants(table).OfType<Button>()
            .First(b => (b.Content?.ToString() ?? "").StartsWith("Email", StringComparison.Ordinal));

        _out.WriteLine($"header hidden after clearing: {HiddenByAncestor(header)}");

        Assert.True(HiddenByAncestor(header));
        Assert.Equal(-1, table.SelectedIndex);
    }

    /// <summary>
    /// The header says what it does. R85 caught it drawing a sort glyph and sorting nothing — a dead
    /// affordance, the same family <c>DeadButtonTests</c> guards on the pages themselves.
    /// </summary>
    [Fact]
    public void TheHeadersActuallySort()
    {
        var table = new AccountTable(new[] { "Email", "Status" }, "Nothing", "Nothing yet");
        table.Rows = new[]
        {
            new[] { "z@example.com", "Active" },
            new[] { "a@example.com", "Inactive" },
            new[] { "m@example.com", "Active" },
        };

        Assert.Equal(-1, table.SortColumn);
        Assert.Equal(new[] { "z@example.com", "a@example.com", "m@example.com" },
            table.Ordered().Select(r => r[0]));

        table.SortBy(0);
        _out.WriteLine("asc:  " + string.Join(",", table.Ordered().Select(r => r[0])));
        Assert.Equal(new[] { "a@example.com", "m@example.com", "z@example.com" },
            table.Ordered().Select(r => r[0]));
        Assert.Contains("Email ↑", Headers(table));

        table.SortBy(0);
        _out.WriteLine("desc: " + string.Join(",", table.Ordered().Select(r => r[0])));
        Assert.Equal(new[] { "z@example.com", "m@example.com", "a@example.com" },
            table.Ordered().Select(r => r[0]));
        Assert.Contains("Email ↓", Headers(table));

        table.SortBy(1);
        Assert.Equal(1, table.SortColumn);
        Assert.True(table.SortAscending);
        Assert.Contains("Status ↑", Headers(table));
        Assert.Contains("Email ⇅", Headers(table));
    }

    // ---------------------------------------------------------------- helpers

    private static List<string> Texts(Control root) =>
        Descendants(root).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();

    private static List<string> Headers(Control root) =>
        Descendants(root).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

    private static bool HiddenByAncestor(Avalonia.StyledElement element)
    {
        for (Avalonia.StyledElement? node = element; node is not null; node = node.Parent)
            if (node is Control control && !control.IsVisible) return true;
        return false;
    }

    private static IEnumerable<Control> Descendants(Control root)
    {
        var queue = new Queue<Control>();
        queue.Enqueue(root);
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (!ReferenceEquals(current, root)) yield return current;

            foreach (var child in Avalonia.LogicalTree.LogicalExtensions
                         .GetLogicalChildren(current).OfType<Control>())
                queue.Enqueue(child);
        }
    }
}
