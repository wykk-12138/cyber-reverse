using System.Collections.Generic;
using System.Threading;
using System.IO;
using System.Threading.Tasks;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 142: the call now has a caller.
///
/// <para>
/// R140 wired Cloudflare, R141 wired Kasada, and both were classes nobody invoked — the same defect one
/// layer down: <b>the call existed and nothing called it</b>. <c>DetectAsync</c> is the single place that
/// knows which wall is in the way, so it is the single place that dispatches.
/// </para>
///
/// <para>
/// The guard is a fact rather than a failure: with no Chromium build the in-bot road cannot run and the
/// service half is unconfigured, so the session records <c>antibot.solver = "unavailable"</c> and the
/// flow continues. That is testable without a browser, which is why it is the behaviour pinned here.
/// </para>
/// </summary>
public sealed class WallDispatchTests
{
    private readonly ITestOutputHelper _out;

    public WallDispatchTests(ITestOutputHelper output) => _out = output;

    private static string Source()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "StoreFlow.cs"));
    }

    /// <summary>Detection dispatches; it no longer stops at storing the vendor.</summary>
    [Fact]
    public void DetectionDispatchesToTheStrategy()
    {
        var text = Source();

        Assert.Contains("return await SolveDetectedWallAsync(c, ct)", text);
        Assert.Contains("protected virtual async Task<StepOutcome> SolveDetectedWallAsync", text);

        // both wired strategies are reachable from here
        Assert.Contains("CloudflareClearance", text);
        Assert.Contains("KasadaClearance", text);
        Assert.Contains("CloudflareStrategyRunner.Default()", text);
        Assert.Contains("KasadaStrategyRunner.Default()", text);
    }

    /// <summary>Only the wired walls are dispatched; the rest are left alone.</summary>
    [Fact]
    public void OnlyWiredWallsAreDispatched()
    {
        var text = Source();

        Assert.Contains("vendor is not (\"cloudflare\" or \"kasada\" or \"datadome\")", text);

        // and the audit agrees: three wired, four gaps
        // R1024: the gaps were three until akamai joined the audit. It is a gap because the image solves it with a
        // three-stage routine this workspace has not written, not because its marker is unsupported -- Gap.None there.
        Assert.Equal(new[] { "cloudflare", "kasada", "datadome" }, Cybersole.Stores.Scripts.VendorWiring.Wired);
        // R1052: six. Gaps is Rows.Where(State != Wired), and two DetectedOnly rows joined.
        Assert.Equal(6, Cybersole.Stores.Scripts.VendorWiring.Gaps.Count);

        _out.WriteLine("dispatch covers exactly the vendors the audit calls wired");
    }

    /// <summary>Without a browser the session records a fact, not a failure.</summary>
    [Fact]
    public async Task WithoutABrowserTheSessionSaysSo()
    {
        var store = new MinimalFlow();
        var context = new FlowContext { Url = "https://example.test/", Http = null! };
        context.Session.Vars["home"] = "<html>cf-chl-</html>";

        var outcome = await store.Detect(context, default);

        Assert.True(outcome.Ok);
        Assert.Equal("cloudflare", context.Session.Vars["antibot"]);

        // the marker decided the vendor; the strategy then either ran or recorded why it could not
        Assert.True(context.Session.Vars.ContainsKey("antibot.solver"));
        Assert.Equal(
            Cybersole.Stores.Scripts.ChromiumBridge.FindBrowser() is null ? "unavailable" : "available",
            context.Session.Vars["antibot.solver"]);

        _out.WriteLine("solver = " + context.Session.Vars["antibot.solver"]);
    }

    /// <summary>A wall nobody wired is detected and left alone.</summary>
    [Fact]
    public async Task AnUnwiredWallIsOnlyDetected()
    {
        var store = new MinimalFlow();
        var context = new FlowContext { Url = "https://example.test/", Http = null! };
        context.Session.Vars["home"] = "<html>_Incapsula_Resource</html>";

        await store.Detect(context, default);

        Assert.Equal("imperva", context.Session.Vars["antibot"]);
        Assert.False(context.Session.Vars.ContainsKey("antibot.solver"));
    }

    /// <summary>The smallest flow that can run detection — the base class's own behaviour.</summary>
    private sealed class MinimalFlow : StoreFlow
    {
        public override string Id => "minimal";
        public override string Name => "minimal";
        public override IReadOnlyList<string> Domains => new[] { "example.test" };

        public Task<StepOutcome> Detect(FlowContext c, CancellationToken ct) => DetectAsync(c, ct);
    }
}
