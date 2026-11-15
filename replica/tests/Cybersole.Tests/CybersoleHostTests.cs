using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 138: the fifteen <c>*.cybersole.io</c> hosts, and what their absence settles.
///
/// <para>
/// The list is a fixture in its own right — it is the original's own infrastructure, and a replica that
/// only models storefronts is modelling the easy half. Four of the fifteen exist to solve a bot wall,
/// which is the same local-versus-service split the Kasada strategy has, and the string
/// <c>Cloudflare solver refused the token, solving in-bot</c> names that split out loud.
/// </para>
///
/// <para>
/// The absence of <c>kasada.cybersole.io</c> is the useful negative: the Kasada <c>Api</c> road has no
/// dedicated host, so its address is either the backend or nothing the image names. The choice of
/// <c>api.cybersole.io</c> is marked as an inference, not a capture.
/// </para>
/// </summary>
public sealed class CybersoleHostTests
{
    private readonly ITestOutputHelper _out;

    public CybersoleHostTests(ITestOutputHelper output) => _out = output;

    /// <summary>Fifteen hosts, all under the domain, all distinct.</summary>
    [Fact]
    public void ThereAreFifteenHosts()
    {
        Assert.Equal(15, CybersoleHosts.All.Count);
        Assert.Equal(15, CybersoleHosts.All.Distinct().Count());
        Assert.All(CybersoleHosts.All,
            h => Assert.EndsWith(".cybersole.io", h, System.StringComparison.Ordinal));

        foreach (var host in CybersoleHosts.All) _out.WriteLine(host);
    }

    /// <summary>There is no dedicated Kasada host — the negative that matters.</summary>
    [Fact]
    public void ThereIsNoKasadaHost()
    {
        Assert.DoesNotContain(CybersoleHosts.All,
            h => h.Contains("kasada", System.StringComparison.OrdinalIgnoreCase));

        Assert.False(CybersoleHosts.IsKnown("kasada.cybersole.io"));
        Assert.True(CybersoleHosts.IsKnown("api.cybersole.io"));
    }

    /// <summary>The API road's candidate is recorded as an inference, with the reason.</summary>
    [Fact]
    public void TheApiRoadCandidateIsLabelled()
    {
        Assert.Equal("api.cybersole.io", CybersoleHosts.KasadaApiCandidate);

        Assert.Contains("no kasada.cybersole.io exists", CybersoleHosts.KasadaApiEvidence);
        Assert.Contains("inferred", CybersoleHosts.KasadaApiEvidence);
        Assert.Contains("no capture", CybersoleHosts.KasadaApiEvidence);

        _out.WriteLine(CybersoleHosts.KasadaApiEvidence);
    }

    /// <summary>Four of the hosts exist to solve a wall, one per wall.</summary>
    [Fact]
    public void FourHostsSolveWalls()
    {
        Assert.Equal(4, CybersoleHosts.SolverHosts.Count);

        foreach (var (host, wall) in CybersoleHosts.SolverHosts)
            _out.WriteLine($"{host,-34} {wall}");

        Assert.Equal("Cloudflare", CybersoleHosts.WallFor("cf-solver.cybersole.io"));
        Assert.Equal("DataDome", CybersoleHosts.WallFor("datadome.cybersole.io"));
        Assert.Equal("Amazon WAF", CybersoleHosts.WallFor("amazon-waf.cybersole.io"));

        Assert.True(CybersoleHosts.IsSolverHost("cf-solver.cybersole.io"));
        Assert.False(CybersoleHosts.IsSolverHost("cdn.cybersole.io"));
        Assert.Null(CybersoleHosts.WallFor("api.cybersole.io"));
    }

    /// <summary>The Cloudflare path has the same service-versus-local split, stated out loud.</summary>
    [Fact]
    public void TheCloudflareSplitIsExplicit()
    {
        Assert.Equal("Cloudflare solver refused the token, solving in-bot",
            CybersoleHosts.CloudflareInBotFallback);

        // the registry the Settings page renders
        Assert.Equal(6, CybersoleHosts.SolverRegistryNames.Count);
        Assert.Contains("CloudflareSolvers", CybersoleHosts.SolverRegistryNames);
        Assert.Contains("CapSolver", CybersoleHosts.SolverRegistryNames);

        // and the strategy's four modes are the general form of this
        Assert.Equal(4, System.Enum.GetValues<KasadaStrategy.Mode>().Length);
    }

    /// <summary>Matching is exact — a lookalike is not "known".</summary>
    [Fact]
    public void KnownIsExact()
    {
        Assert.True(CybersoleHosts.IsKnown("api.cybersole.io"));
        Assert.False(CybersoleHosts.IsKnown("api.cybersole.io.evil.test"));
        Assert.False(CybersoleHosts.IsKnown(null));
    }
}
