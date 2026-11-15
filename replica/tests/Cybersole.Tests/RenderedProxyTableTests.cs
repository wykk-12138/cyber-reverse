using Avalonia.Controls;
using System.Reflection;
using Cybersole.Core;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 66: the first round that drove the real window instead of reading the model.
///
/// Three defects came out of it, and none of them were visible to the tests that existed:
///
///   1. <c>Clear Failed</c> / <c>Clear Over</c> rendered between the column headers and the rows,
///      because DockPanel order is child order and the actions were added after the header.
///   2. The Status column printed <c>Cybersole.Core.Models.Status</c> — the type name — because
///      the cell used <c>proxy.Status.ToString()</c> on a class with no override.
///   3. <c>Reset limits after</c> showed "ThirtyMinutes" for a group whose UsageExpiry was null,
///      while the caption beside it said "No reset window".
///
/// Each test below asserts the rendered thing, not the model. That is the difference that let all
/// three survive until a screenshot.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class RenderedProxyTableTests
{
    private readonly ITestOutputHelper _out;

    public RenderedProxyTableTests(ITestOutputHelper output) => _out = output;

    private static Proxy Make(string host, string status = "Idle", int usage = 0) => new()
    {
        Host = host,
        Port = 8080,
        Username = "u",
        Password = "p",
        Status = new Status { Text = status },
        Usage = usage,
    };

    /// <summary>
    /// Every cell's text, read off the built control tree. This is what a user sees.
    /// </summary>
    private static List<string> CellTexts(ProxyGrid view)
    {
        var root = (DockPanel)view.Content!;
        var scroll = root.Children.OfType<ScrollViewer>().Single();
        var body = (StackPanel)scroll.Content!;
        var row = body.Children.OfType<Grid>().First();

        return row.Children.OfType<TextBlock>().Select(t => t.Text ?? string.Empty).ToList();
    }

    /// <summary>
    /// The Status cell renders the label. The type name appearing here is what a screenshot found.
    /// </summary>
    [Fact]
    public void TheStatusCellShowsTheLabelNotTheTypeName()
    {
        var view = new ProxyGrid(new List<Proxy> { Make("10.0.0.1", status: "Failed") });
        var cells = CellTexts(view);

        _out.WriteLine($"cells: {string.Join(" | ", cells)}");

        Assert.Contains("Failed", cells);
        Assert.DoesNotContain("Cybersole.Core.Models.Status", cells);
        Assert.DoesNotContain(cells, c => c.Contains("Models.Status", StringComparison.Ordinal));
    }

    /// <summary>
    /// <c>Status.ToString()</c> returns the label, so any future cell or interpolation that uses
    /// it renders something readable.
    /// </summary>
    [Fact]
    public void TheStatusObjectPrintsItsLabel()
    {
        var s = new Status { Text = "Running" };

        _out.WriteLine($"ToString() = {s}");
        _out.WriteLine($"interpolated = {s}");

        Assert.Equal("Running", s.ToString());
        Assert.Equal("Running", $"{s}");
    }

    /// <summary>
    /// The toolbar shares the header row, and the table has the four columns the locale names.
    ///
    /// <para>
    /// R72: this test used to assert the opposite — a toolbar as its own row above five column
    /// headers, the fifth being <c>Usage</c>. Driving the live 5.18.32 showed one header line
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

        // The select-all CheckBox is a Button subclass with no text content; it is not a column.
        var labels = header.Children.OfType<Button>()
            .Select(b => (b.Content as TextBlock)?.Text ?? string.Empty)
            .Where(text => text.Length > 0)
            .ToList();

        _out.WriteLine("header: " + string.Join(",", labels));

        // The first column is the one the table is already sorted by, so it carries the glyph.
        Assert.Equal(new[] { "IP ↑", "Port", "Username", "Status" }, labels);
    }

    /// <summary>
    /// A group with no UsageExpiry shows "(none)", not the first enum value.
    ///
    /// The dialog and the caption have to agree: "No reset window — limits do not roll over" is a
    /// lie if the box above it says ThirtyMinutes.
    /// </summary>
    [Fact]
    public void AnUnsetResetWindowShowsNone()
    {
        var group = new ProxyGroup { Name = "G", UsageExpiry = null };
        var view = new ProxyGroupView(group);

        var combo = FindCombo(view, "Reset limits after");
        Assert.NotNull(combo);
        var items = combo!.ItemsSource!.Cast<object>().Select(o => o.ToString()).ToList();

        _out.WriteLine($"items: {string.Join(",", items)}");
        _out.WriteLine($"selected: {combo.SelectedItem}");

        Assert.Equal("(none)", items[0]);
        Assert.Equal("(none)", combo.SelectedItem?.ToString());
        Assert.Equal(8, items.Count);   // (none) + 7 TimeSpans
    }

    /// <summary>Choosing a real duration writes the enum, choosing (none) clears it.</summary>
    [Fact]
    public void ChoosingADurationAndThenNoneRoundTrips()
    {
        var group = new ProxyGroup { Name = "G" };
        var view = new ProxyGroupView(group);
        var combo = FindCombo(view, "Reset limits after")!;

        combo.SelectedIndex = 1;   // first real value
        _out.WriteLine($"after index 1: {group.UsageExpiry}");
        Assert.Equal(TimeSpans.ThirtyMinutes, group.UsageExpiry);

        combo.SelectedIndex = 6;   // OneDay
        _out.WriteLine($"after index 6: {group.UsageExpiry}");
        Assert.Equal(TimeSpans.OneDay, group.UsageExpiry);

        combo.SelectedIndex = 0;   // (none)
        _out.WriteLine($"after index 0: {(group.UsageExpiry is null ? "(null)" : group.UsageExpiry.ToString())}");
        Assert.Null(group.UsageExpiry);
    }

    /// <summary>Finds the ComboBox on the row whose label matches.</summary>
    /// <remarks>
    /// UiKit.Row builds a two-column Grid (label in column 0, input in column 1) — not a
    /// StackPanel. Guessing StackPanel found nothing and reported "no such row", which is the
    /// same class of mistake as reading a control tree by eye.
    /// </remarks>
    private static ComboBox? FindCombo(Control view, string label)
    {
        var body = ((UserControl)view).Content;
        if (body is not Control root) return null;

        foreach (var row in FindAll<Grid>(root).Where(g => g.Children.Count == 2))
        {
            if (row.Children[0] is not TextBlock text) continue;
            if (text.Text != label) continue;
            return row.Children[1] as ComboBox;
        }

        return null;
    }

    private static IEnumerable<Control> Kids(Control root)
    {
        switch (root)
        {
            case Panel p:
                foreach (var c in p.Children) yield return c;
                break;
            // ScrollViewer derives from ContentControl, so it must be matched first.
            case ScrollViewer s when s.Content is Control sc:
                yield return sc;
                break;
            case ContentControl c when c.Content is Control cc:
                yield return cc;
                break;
            case Decorator d when d.Child is Control dc:
                yield return dc;
                break;
        }
    }

    private static T? FindFirst<T>(Control root) where T : Control
    {
        if (root is T hit) return hit;
        foreach (var kid in Kids(root))
        {
            var found = FindFirst<T>(kid);
            if (found is not null) return found;
        }
        return null;
    }

    private static IEnumerable<T> FindAll<T>(Control root) where T : Control
    {
        if (root is T hit) yield return hit;
        foreach (var kid in Kids(root))
            foreach (var found in FindAll<T>(kid))
                yield return found;
    }
}
