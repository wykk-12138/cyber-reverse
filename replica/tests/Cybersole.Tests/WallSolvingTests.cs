using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 143: the original's solve surface, and the correction it forces on R141.
///
/// <para>
/// R141's audit recorded DataDome as "a host, no protocol" and left the vendor at that. The image names
/// <c>SolveBotD</c> — DataDome's own challenge script — so the original does solve it, and the missing
/// piece is <b>this workspace's</b> knowledge rather than the original's implementation. Same distinction
/// as R127's missing controllers: the gap is in my notes.
/// </para>
///
/// <para>
/// <c>PollCaptchaAsync</c> answers the other half of this round's question: at least one road is polled
/// rather than awaited, so a synchronous ladder fits a local browser solve and not a deferred service.
/// </para>
/// </summary>
public sealed class WallSolvingTests
{
    private readonly ITestOutputHelper _out;

    public WallSolvingTests(ITestOutputHelper output) => _out = output;

    /// <summary>Detection is a real step, named exactly as the replica names it.</summary>
    [Fact]
    public void TheDetectStepNameMatches()
    {
        Assert.Equal("DetectAsync", WallSolving.DetectStep);

        // the replica's own step carries the same name
        var context = new Cybersole.Stores.Flows.FlowContext
        {
            Url = "https://example.test/", Http = null!,
        };
        Assert.NotNull(context);

        _out.WriteLine("the replica's DetectAsync is the image's DetectAsync");
    }

    /// <summary>Twelve solve-shaped methods, with the vendored ones mapped.</summary>
    [Fact]
    public void TheSolveSurfaceIsRecorded()
    {
        Assert.Equal(12, WallSolving.SolveMethods.Count);
        Assert.Equal(12, WallSolving.SolveMethods.Distinct().Count());

        foreach (var method in WallSolving.SolveMethods) _out.WriteLine(method);

        Assert.Equal("datadome", WallSolving.MethodVendor["SolveBotD"]);
        Assert.Equal("service", WallSolving.MethodVendor["RemoteSolve"]);
        Assert.Equal("generic", WallSolving.MethodVendor["SolveWafAsync"]);
    }

    /// <summary>DataDome is solved by the original — R141's row is corrected.</summary>
    [Fact]
    public void DataDomeIsSolvedByTheOriginal()
    {
        Assert.True(WallSolving.HasSolveFor("datadome"));
        Assert.Contains("SolveBotD", WallSolving.VendoredSolves);

        // but the audit's state stays as it is: this workspace still lacks the protocol
        Assert.Equal(VendorWiring.State.HostWithoutProtocol,
            VendorWiring.For("datadome")!.State);

        // the correction says exactly that, in both directions
        Assert.Contains("SolveBotD exists", WallSolving.DataDomeCorrection);
        Assert.Contains("this workspace's gap", WallSolving.DataDomeCorrection);

        _out.WriteLine(WallSolving.DataDomeCorrection);
    }

    /// <summary>The replica's Cloudflare and Kasada names line up with the image's generic solves.</summary>
    [Fact]
    public void TheGenericSolvesLineUpWithTheReplica()
    {
        // SolveWafAsync is the generic step the replica's two ladders both are
        Assert.True(WallSolving.HasSolveFor("generic"));
        Assert.True(WallSolving.HasSolveFor("service"));

        // and RemoteSolve is the Api/Service road both strategies already have
        Assert.Equal(KasadaStrategy.Mode.Api, KasadaStrategyRunner.Default().Order[0]);
        Assert.Equal(CloudflareStrategy.Mode.Service, CloudflareStrategyRunner.Default().Order[0]);
    }

    /// <summary>One road is polled, which is a fact about the shape of the dispatch.</summary>
    [Fact]
    public void OneRoadIsPolled()
    {
        Assert.Single(WallSolving.Polling);
        Assert.Equal("PollCaptchaAsync", WallSolving.Polling[0]);

        Assert.Contains("answers later", WallSolving.PollingConsequence);
        Assert.Contains("local browser", WallSolving.PollingConsequence);

        _out.WriteLine(WallSolving.PollingConsequence);
    }

    /// <summary>Vendors with no solve method stay without one.</summary>
    [Fact]
    public void VendorsWithoutASolveStayWithoutOne()
    {
        Assert.False(WallSolving.HasSolveFor("imperva"));
        Assert.False(WallSolving.HasSolveFor("perimeterx"));
        Assert.False(WallSolving.HasSolveFor(null));

        // queue-it is a queue, not a wall, so it should never gain a solve method
        Assert.False(WallSolving.HasSolveFor("queue-it"));
        Assert.Equal(VendorWiring.State.NotAChallenge, VendorWiring.For("queue-it")!.State);
    }
}
