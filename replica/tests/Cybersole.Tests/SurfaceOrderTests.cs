using System.IO;
using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 168: the composition order becomes a contract.
///
/// <para>
/// Three rounds learned it the expensive way — a mask that ran before its getters, an engine block that lost its
/// plugins to an older patch, an install that broke a reseat. The order is written down here so the fourth mistake
/// fails a test in milliseconds instead of a runtime measurement in seconds.
/// </para>
/// </summary>
public sealed class SurfaceOrderTests
{
    private readonly ITestOutputHelper _out;

    public SurfaceOrderTests(ITestOutputHelper output) => _out = output;

    private static string Bridge() => File.ReadAllText(Path.Combine(RepoRoot(), "src",
        "Cybersole.Stores", "Scripts", "ChromiumBridge.cs"));

    /// <summary>The bridge's composition matches the contract.</summary>
    [Fact]
    public void TheBridgeFollowsTheOrder()
    {
        var problems = SurfaceOrder.Check(Bridge());

        Assert.True(problems.Count == 0, string.Join(" | ", problems));
    }

    /// <summary>Sixteen steps, each with a reason that is not "it was easier".</summary>
    [Fact]
    public void TheStepsCarryTheirReasons()
    {
        Assert.Equal(24, SurfaceOrder.Steps.Count);
        Assert.Equal(new[]
        {
            "capture", "mask", "parity", "engine", "webassembly", "mobile", "touches", "prune", "locks", "reseat",
            "window-names", "window-order", "window-order-wrap", "global-prune", "document-prune", "css-properties", "canvas", "webgl", "global-surface", "handlers", "match-media", "fonts-media", "mask-pass", "baseline-snapshot",
        }, SurfaceOrder.Names);

        foreach (var step in SurfaceOrder.Steps)
        {
            Assert.False(string.IsNullOrWhiteSpace(step.Why));
            _out.WriteLine($"{step.Position}. {step.Name,-12} {step.Why}");
        }
    }

    /// <summary>A deliberately wrong order is rejected, with the reason quoted back.</summary>
    [Fact]
    public void AWrongOrderIsRejected()
    {
        // the reseat before the locks install is exactly R167's mistake
        var wrong = """
                    var surfaceBody = NativeRefs.BodyJs() + NativeMask.BodyJs();
                    surfaceBody += EngineParity.BodyJs();
                    surfaceBody += MobileSurface.EngineBodyJs();
                    surfaceBody += WebAssemblySurface.BodyJs();
                    surfaceBody += MobileSurface.BodyJs();
                    surfaceBody += MobileNavigator.BodyJs(userAgent);
                    surfaceBody += NavPrune.BodyJs();
                    surfaceBody += NavOrder.ReseatBodyJs(NavOrder.Navigator);
                    surfaceBody += NavigatorLocks.BodyJs();
                    surfaceBody += WindowBaseline.BodyJs();
                    surfaceBody += WindowOrder.BodyJs();
                    surfaceBody += WindowOrderWrap.BodyJs();
                    surfaceBody += GlobalPrune.GlobalBodyJs();
                    surfaceBody += GlobalPrune.DocumentBodyJs();
                    surfaceBody += CssStyleProperties.BodyJs();
                    surfaceBody += CanvasSurface.BodyJs();
                    surfaceBody += WebGlSurface.BodyJs();
                    surfaceBody += GlobalSurface.BodyJs();
                    surfaceBody += HandlerSurface.BodyJs();
                    surfaceBody += MediaQuerySurface.BodyJs();
                    surfaceBody += FontMediaSurface.BodyJs();
                    surfaceBody += MaskTargets.ApplyJs();
                    surfaceBody += WindowBaselineSnapshot.BodyJs();
                    """;

        var problems = SurfaceOrder.Check(wrong);

        Assert.NotEmpty(problems);
        Assert.Contains(problems, p => p.Contains("reseat appears before locks", System.StringComparison.Ordinal));
        _out.WriteLine(problems[0]);
    }

    /// <summary>A missing body is rejected too, rather than silently passing.</summary>
    [Fact]
    public void AMissingBodyIsRejected()
    {
        var missing = Bridge().Replace("surfaceBody += MaskTargets.ApplyJs();", 
            "// the mask pass was removed", System.StringComparison.Ordinal);

        var problems = SurfaceOrder.Check(missing);

        Assert.Contains(problems, p => p.Contains("mask-pass: marker not found", System.StringComparison.Ordinal));
    }

    /// <summary>The rule says what the three rounds cost.</summary>
    [Fact]
    public void TheRuleStands()
    {
        Assert.Contains("position is semantics", SurfaceOrder.Rule);
        Assert.Contains("installs, orders, deletes or masks", SurfaceOrder.Rule);
        Assert.Contains("where its verb allows", SurfaceOrder.Rule);
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir!.FullName;
    }
}
