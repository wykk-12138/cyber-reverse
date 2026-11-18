using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the interrogation path is only worth having if a flow actually uses it. Before this was
/// wired, NikeFlow's script branch constructed a KasadaSolver with no resourceAddress and no transport,
/// which meant the sensor never interrogated anything and the branch failed on every run — so the browser
/// was always the only source. These cases pin the wiring: the origin the sensor is configured with, and
/// that the flow-level call now supplies both pieces.
/// </summary>
public sealed class KasadaFlowWiringTests
{
    [Theory]
    [InlineData("https://www.nike.com/launch", "https://www.nike.com/")]
    [InlineData("https://www.nike.com", "https://www.nike.com/")]
    [InlineData("https://api.nike.com/abc/def/p.js", "https://api.nike.com/")]
    [InlineData("http://127.0.0.1:8080/x/y", "http://127.0.0.1:8080/")]
    public void TheOriginIsWhatTheSensorIsConfiguredWith(string url, string expected)
    {
        Assert.Equal(expected, KasadaSolver.OriginOf(url));
    }

    [Theory]
    [InlineData("https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
        "https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/")]
    [InlineData("https://www.nike.com/p.js", "https://www.nike.com/")]
    [InlineData("https://www.nike.com/launch", "https://www.nike.com/")]
    public void TheSensorIsConfiguredWithTheDirectoryItsScriptCameFrom(string url, string expected)
    {
        // Measured against the live site: GET /mfc and GET /r answer 200 only under the script's own
        // directory; the bare origin answers 404. The UUID segments are part of the address.
        Assert.Equal(expected, KasadaSolver.ResourceAddressOf(url));
    }

    [Fact]
    public void AMalformedUrlAnswersNullRatherThanThrowing()
    {
        // OriginOf sits in a fallback chain in the flow, so it must not throw on a relative script src or
        // an empty session var -- both are reachable states.
        Assert.Null(KasadaSolver.OriginOf(null));
        Assert.Null(KasadaSolver.OriginOf(""));
        Assert.Null(KasadaSolver.OriginOf("/p.js"));
        Assert.Null(KasadaSolver.OriginOf("not a url"));
    }

    [Fact]
    public void TheNikeFlowConstructsASolverThatCanActuallyInterrogate()
    {
        // Source-level check on purpose: the failure mode this guards is a call site that constructs the
        // solver correctly but omits the two properties that make it work, which no behavioural test in
        // this offline suite can observe (it would need a live endpoint).
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        var flowDir = Path.GetFullPath(Path.Combine(dir!, "..", "..", "..", "..", "..", "src",
            "Cybersole.Stores", "Flows"));
        var source = File.ReadAllText(Path.Combine(flowDir, "NikeFlow.cs"));

        Assert.Contains("ResourceAddress = origin", source, StringComparison.Ordinal);
        Assert.Contains("KasadaSolver.NetTransport(", source, StringComparison.Ordinal);
        Assert.Contains("Store = \"nike\"", source, StringComparison.Ordinal);

        // A sync-over-async transport call must not run on the flow's own thread.
        Assert.Contains("await Task.Run(() => solver.Solve(script), ct)", source, StringComparison.Ordinal);
    }
}
