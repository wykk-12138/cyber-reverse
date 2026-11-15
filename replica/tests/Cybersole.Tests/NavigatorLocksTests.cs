using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 167: two of the thirteen get installed, on the prototype and masked.
///
/// <para>
/// <c>standalone</c> is a Safari-only boolean and <c>locks</c> is the Web Locks API — both answerable without a lock
/// manager, because a page that calls <c>request</c> wants its callback to run. They go on
/// <c>Navigator.prototype</c> per R164 and into the mask table per R160: a member that exists and prints its own source
/// answers two questions wrongly, which is worse than answering one.
/// </para>
/// </summary>
public sealed class NavigatorLocksTests
{
    private readonly ITestOutputHelper _out;

    public NavigatorLocksTests(ITestOutputHelper output) => _out = output;

    /// <summary>The body installs both on the prototype.</summary>
    [Fact]
    public void TheBodyUsesThePrototype()
    {
        var js = NavigatorLocks.BodyJs();

        Assert.Contains("Object.getPrototypeOf(N)", js);
        Assert.Contains("Object.defineProperty(P, 'standalone'", js);
        Assert.Contains("Object.defineProperty(P, 'locks'", js);
        Assert.Contains("!('locks' in P)", js);
        Assert.Contains("Promise.resolve", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
        _out.WriteLine($"{js.Length} characters");
    }

    /// <summary>The arities are the specification's.</summary>
    [Fact]
    public void TheAritiesAreTheSpecifications()
    {
        Assert.Equal(2, NavigatorLocks.RequestArity);
        Assert.Equal(0, NavigatorLocks.QueryArity);
        Assert.Equal(2, NativeArity.For("request"));
        Assert.Equal(0, NativeArity.For("query"));

        // and the mask table covers the two members themselves
        var getters = MaskTargets.Getters.Select(t => t.Property).ToList();
        Assert.Contains("standalone", getters);
        Assert.Contains("locks", getters);
    }

    /// <summary>Both names are on the census's missing list, and now installed.</summary>
    [Fact]
    public void TheTwoNamesComeFromTheThirteen()
    {
        Assert.Equal(new[] { "standalone", "locks" }, NavigatorLocks.Installed);
        Assert.All(NavigatorLocks.Installed, n => Assert.Contains(n, NavigatorCensus.Missing));
        Assert.Equal(NavigatorCensus.InstalledNow, NavigatorLocks.Installed);
    }

    /// <summary>Measured: the members exist, answer, and look native.</summary>
    [Fact]
    public async Task TheMembersExistAndLookNative()
    {
        const string iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                              "Mobile/15E148 Safari/604.1";

        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: iphone);
        await bridge.ApplyStealthAsync(iphone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([navigator.standalone, typeof navigator.locks, " +
            "typeof navigator.locks.request, navigator.locks.request.length, " +
            "typeof navigator.locks.query, navigator.locks.query.length])");

        _out.WriteLine("probe = " + probe);
        Assert.Equal("[false,\"object\",\"function\",2,\"function\",0]", probe);

        // The callback runs, which is what a page calls request for. Evaluated synchronously: an async IIFE
        // returns a promise, and the bridge answers the promise object rather than its value (R167 — the
        // first version of this assertion read "{}").
        var ran = await bridge.EvaluateAsync(
            "(() => { let ran = false; " +
            "const p = navigator.locks.request('t', () => { ran = true; return 7; }); " +
            "return String(p instanceof Promise) + ':' + String(ran); })()");
        Assert.Equal("true:true", ran);

        // and query() resolves to an empty snapshot
        var snapshot = await bridge.EvaluateAsync(
            "(() => { const q = navigator.locks.query(); " +
            "return String(q instanceof Promise) + ':' + (typeof q.then === 'function'); })()");
        Assert.Equal("true:true", snapshot);

        // and neither announces itself
        var masked = await bridge.EvaluateAsync(
            "JSON.stringify([Function.prototype.toString.call(" +
            "Object.getOwnPropertyDescriptor(Object.getPrototypeOf(navigator), 'locks').get), " +
            "Function.prototype.toString.call(navigator.locks.request)])");
        Assert.DoesNotContain("function (", masked!, System.StringComparison.Ordinal);
        _out.WriteLine("masked = " + masked);
    }
}
