using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 59: <c>Proxies.More.TestOn</c> ("Test On:") is the per-row counterpart of "Test All On".
/// R58 gave the tester a target; this round gives the row a way to use it.
///
/// The menu item is only offered when a tester was supplied. A row menu that shows "Test Proxies" and
/// does nothing is worse than a row menu without it — the user cannot tell which state they are in.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class ProxyRowTestTests
{
    private readonly ITestOutputHelper _out;

    public ProxyRowTestTests(ITestOutputHelper output) => _out = output;

    private static Proxy Make(string host) => new()
    {
        Host = host,
        Port = 8080,
        Status = new Status { Text = "Idle" },
    };

    /// <summary>
    /// Supplying a tester makes the row menu offer "Test Proxies", and invoking it runs that tester
    /// with that row's proxy.
    /// </summary>
    [Fact]
    public void TheRowMenuTestsThatRow()
    {
        var proxy = Make("10.0.0.1");
        var asked = new List<Proxy>();

        var view = new ProxyGrid(new List<Proxy> { proxy })
            .WithTester(p => { asked.Add(p); return Task.CompletedTask; });

        var labels = MenuLabels(view);
        _out.WriteLine($"menu: {string.Join(" | ", labels)}");

        Assert.Contains("Test Proxies", labels);

        // Calls the same method the menu item binds. Raising the routed Click event instead
        // passed alone and failed in the suite: it needs a dispatcher the suite does not have.
        view.TestProxy(proxy);

        _out.WriteLine($"tester saw: {string.Join(",", asked.Select(p => p.Host))}");
        Assert.Single(asked);
        Assert.Same(proxy, asked[0]);
    }

    /// <summary>
    /// With no tester, the item is absent. The row menu still carries Copy and Delete — the point
    /// is that "Test Proxies" specifically is not offered as a dead entry.
    /// </summary>
    [Fact]
    public void WithoutATesterThereIsNoTestOnItem()
    {
        var view = new ProxyGrid(new List<Proxy> { Make("10.0.0.2") });

        var labels = MenuLabels(view);
        _out.WriteLine($"menu: {string.Join(" | ", labels)}");

        Assert.DoesNotContain("Test Proxies", labels);
        Assert.Contains("Copy Proxies", labels);
        Assert.Contains("Delete Proxies", labels);
    }

    /// <summary>
    /// Reads the header of every MenuItem in the first row's context menu.
    /// </summary>
    private static List<string> MenuLabels(ProxyGrid view)
    {
        var row = FirstRow(view);
        Assert.NotNull(row.ContextMenu);
        return row.ContextMenu!.ItemsSource!.Cast<object>()
            .OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? string.Empty)
            .ToList();
    }


    private static Control FirstRow(ProxyGrid view)
    {
        var root = (DockPanel)view.Content!;
        var scroll = root.Children.OfType<ScrollViewer>().Single();
        var body = (StackPanel)scroll.Content!;
        return body.Children.OfType<Grid>().First();
    }
}
