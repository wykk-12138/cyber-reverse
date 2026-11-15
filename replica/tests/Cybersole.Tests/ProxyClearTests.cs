using Cybersole.Core.Models;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 57: <c>Proxies.More.ClearFailed</c> and <c>Proxies.More.ClearOverFormat</c> were locale
/// actions with no implementation. ClearOver only became meaningful once usage was a visible
/// column (R56) — before that the page showed traffic, and there was nothing to compare a limit
/// against.
///
/// These tests call the view's own logic through the real controls rather than re-deriving it, so
/// a change to the predicate fails here instead of in production.
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class ProxyClearTests
{
    private readonly ITestOutputHelper _out;

    public ProxyClearTests(ITestOutputHelper output) => _out = output;

    private static Proxy Make(string host, string status, int usage = 0) => new()
    {
        Host = host,
        Port = 8080,
        Username = "u",
        Password = "p",
        Status = new Status { Text = status },
        Usage = usage,
    };

    private static IList<Proxy> List(params Proxy[] items) => new List<Proxy>(items);

    /// <summary>
    /// ClearOver removes exactly the proxies at or past the limit, and leaves the rest.
    ///
    /// The comparison is <c>&gt;=</c>, not <c>&gt;</c>: a proxy that has been used exactly as many
    /// times as allowed is spent. Treating it as still-usable would keep handing it out.
    /// </summary>
    [Fact]
    public void ClearOverRemovesTheSpentOnes()
    {
        var proxies = List(
            Make("a", "Idle", usage: 0),
            Make("b", "Idle", usage: 4),
            Make("c", "Idle", usage: 5),
            Make("d", "Idle", usage: 9));

        var view = new ProxyGrid(proxies).WithUsageLimit(5);
        var cleared = Invoke(view, "ClearOver");

        var left = string.Join(",", proxies.Select(p => p.Host));
        _out.WriteLine($"left after ClearOver(limit=5): [{left}]  cleared={cleared}");

        Assert.Equal("a,b", left);
    }

    /// <summary>A null or zero limit means unlimited: ClearOver must not delete everything.</summary>
    [Theory]
    [InlineData(null)]
    [InlineData(0)]
    public void ClearOverDoesNothingWithoutALimit(int? limit)
    {
        var proxies = List(Make("a", "Idle", usage: 99), Make("b", "Idle", usage: 1));

        var view = new ProxyGrid(proxies).WithUsageLimit(limit);
        Invoke(view, "ClearOver");

        _out.WriteLine($"limit={limit}: left={proxies.Count}");
        Assert.Equal(2, proxies.Count);
    }

    /// <summary>
    /// ClearFailed removes only the rows whose status text is "Failed".
    ///
    /// <c>Status</c> is a pill object (Text/Color/Icon) with static Idle/Running/Failed/Success
    /// instances, not an enum, so the predicate compares Text. A row that is merely Idle is not a
    /// failure and must survive.
    /// </summary>
    [Fact]
    public void ClearFailedRemovesOnlyFailures()
    {
        var proxies = List(
            Make("a", "Failed"),
            Make("b", "Idle"),
            Make("c", "Success"),
            Make("d", "Failed"));

        var view = new ProxyGrid(proxies);
        Invoke(view, "ClearFailed");

        var left = string.Join(",", proxies.Select(p => p.Host));
        _out.WriteLine($"left after ClearFailed: [{left}]");
        Assert.Equal("b,c", left);
    }

    /// <summary>
    /// Both actions mutate the list they were handed. A copy would make them look like they
    /// worked while the model kept every proxy — the failure mode the live-list constructor is
    /// there to prevent.
    /// </summary>
    [Fact]
    public void TheActionsMutateTheCallersList()
    {
        var proxies = List(Make("a", "Failed"));
        var changed = 0;

        var view = new ProxyGrid(proxies, () => changed++);
        Invoke(view, "ClearFailed");

        _out.WriteLine($"caller's list count={proxies.Count} onChanged={changed}");

        Assert.Empty(proxies);
        Assert.Equal(1, changed);
    }

    /// <summary>
    /// Calls the private handler by name. The alternative — exposing it — would widen the public
    /// surface of a view just to make it testable, and a view that only ever gets called by its
    /// own button does not need that.
    /// </summary>
    private static object? Invoke(ProxyGrid view, string method)
    {
        var info = typeof(ProxyGrid).GetMethod(method,
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
        Assert.NotNull(info);
        return info!.Invoke(view, null);
    }
}
