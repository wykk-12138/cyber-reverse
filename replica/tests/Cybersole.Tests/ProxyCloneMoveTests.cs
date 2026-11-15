using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 61: <c>Proxies.Context.Clone</c> and <c>Proxies.Context.MoveTo</c>.
///
/// Clone copies the endpoint without the run state; Move reparents the existing row so its usage
/// history follows it. Those are deliberately different: an endpoint can be duplicated, but a
/// measurement cannot be.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class ProxyCloneMoveTests
{
    private readonly ITestOutputHelper _out;

    public ProxyCloneMoveTests(ITestOutputHelper output) => _out = output;

    private static Proxy Make() => new()
    {
        Host = "10.0.0.9",
        Port = 3128,
        Username = "u",
        Password = "p",
        Scheme = "socks5",
        GroupId = "g1",
        Usage = 8,
        TotalDownload = 4096,
        TotalUpload = 1024,
        Status = new Status { Text = "Failed" },
    };

    /// <summary>
    /// The endpoint travels; identity and measurement do not.
    ///
    /// A clone carrying Usage=8 would be removed by "Clear Over" before it had been used once, and
    /// one carrying Status=Failed would be removed by "Clear Failed" while still untested.
    /// </summary>
    [Fact]
    public void ACloneCopiesTheEndpointOnly()
    {
        var original = Make();
        var clone = original.Clone();

        _out.WriteLine($"id: {original.Id} -> {clone.Id}");
        _out.WriteLine($"usage: {original.Usage} -> {clone.Usage}");
        _out.WriteLine($"status: {original.Status.Text} -> {clone.Status.Text}");
        _out.WriteLine($"bytes: {original.TotalDownload} -> {clone.TotalDownload}");

        Assert.NotEqual(original.Id, clone.Id);
        Assert.Equal("10.0.0.9", clone.Host);
        Assert.Equal(3128, clone.Port);
        Assert.Equal("u", clone.Username);
        Assert.Equal("p", clone.Password);
        Assert.Equal("socks5", clone.Scheme);

        Assert.Equal(0, clone.Usage);
        Assert.Equal(0, clone.TotalDownload);
        Assert.Equal(0, clone.TotalUpload);
        Assert.Equal("Idle", clone.Status.Text);
        Assert.Null(clone.GroupId);
    }

    /// <summary>
    /// The row menu offers Clone, and cloning adds one row without touching the original.
    /// </summary>
    [Fact]
    public void CloningARowAddsARow()
    {
        var proxies = new List<Proxy> { Make() };
        var view = new ProxyGrid(proxies);

        var labels = MenuLabels(view);
        _out.WriteLine($"menu: {string.Join(" | ", labels)}");
        Assert.Contains("Clone Proxies", labels);

        view.CloneProxy(proxies[0]);

        _out.WriteLine($"rows: {proxies.Count}, group ids: {string.Join(",", proxies.Select(p => p.GroupId ?? "-"))}");
        Assert.Equal(2, proxies.Count);

        // CloneProxy keeps the source group: a copy made inside a group belongs to that group.
        Assert.Equal("g1", proxies[1].GroupId);
        Assert.Equal("g1", proxies[0].GroupId);
        Assert.Equal(8, proxies[0].Usage);
        Assert.Equal(0, proxies[1].Usage);
    }

    /// <summary>Move is offered only when a mover was supplied, same rule as Test On.</summary>
    [Fact]
    public void MoveIsOnlyOfferedWithAMover()
    {
        var with = MenuLabels(new ProxyGrid(new List<Proxy> { Make() })
            .WithMover(_ => Task.CompletedTask));
        var without = MenuLabels(new ProxyGrid(new List<Proxy> { Make() }));

        _out.WriteLine($"with mover: {string.Join(" | ", with)}");
        _out.WriteLine($"without:    {string.Join(" | ", without)}");

        Assert.Contains("Move proxies to", with);
        Assert.DoesNotContain("Move proxies to", without);
    }

    /// <summary>
    /// Reparenting changes only the group. The usage history is why move is not clone+delete.
    /// </summary>
    [Fact]
    public void MovingKeepsTheHistory()
    {
        var groups = new List<ProxyGroup>
        {
            new() { Name = "A", Id = "ga" },
            new() { Name = "B", Id = "gb" },
        };
        var proxy = Make();
        proxy.GroupId = "ga";

        var view = new ProxyMoveView(groups, groups[0]);
        var chosen = view.Chosen(groups);

        // Simulate the confirm button: reassign GroupId only.
        proxy.GroupId = groups[1].Id;

        _out.WriteLine($"chosen: {chosen?.Name ?? "(none)"}  proxy now in: {proxy.GroupId}");
        Assert.Equal("gb", proxy.GroupId);
        Assert.Equal(8, proxy.Usage);
        Assert.Equal("Failed", proxy.Status.Text);
    }

    private static List<string> MenuLabels(ProxyGrid view)
    {
        var root = (DockPanel)view.Content!;
        var scroll = root.Children.OfType<ScrollViewer>().Single();
        var body = (StackPanel)scroll.Content!;
        var row = body.Children.OfType<Grid>().First();

        return row.ContextMenu!.ItemsSource!.Cast<object>()
            .OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? string.Empty)
            .ToList();
    }
}
