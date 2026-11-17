using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1029: the single How column answered two questions at once and was wrong twice for it, so it becomes two axes.
///
/// <para>
/// Cloudflare is the case that made one value impossible. A user supplies an ApiKey and the app displays a balance, so
/// a paid third party solves; and the same vendor is warmed through cf-solver.cybersole.io, so the original relays too.
/// R1027 recorded the relaying and lost the solver; R1026 recorded neither. Split, both facts fit.
/// </para>
///
/// <para>
/// Kasada and Akamai are deliberately left as Solver.Unknown. Their vocabulary says "API down (Contact staff)", which
/// establishes that somebody else solves, and nothing establishes who. Reusing UserThirdParty on that evidence would be
/// the same inference that has been wrong twice -- so the column says it does not know.
/// </para>
/// </summary>
public sealed class VendorSolvingModeTests
{
    /// <summary>The paid-third-party solver is Cloudflare, evidenced by its property set rather than a host.</summary>
    [Fact]
    public void CloudflareIsSolvedByAUserSuppliedService()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "cloudflare");

        Assert.Equal(VendorWiring.Solver.UserThirdParty, row.Solver);
        Assert.True(row.Relayed);
    }

    /// <summary>DataDome is the opposite arrangement: the original's own service, not a user's key.</summary>
    [Fact]
    public void DataDomeIsSolvedByTheOriginalsOwnService()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "datadome");

        Assert.Equal(VendorWiring.Solver.SelfHosted, row.Solver);
        Assert.True(row.Relayed);
    }

    /// <summary>
    /// Kasada and Akamai know that somebody else solves but not who, so they say Unknown rather than borrowing a value.
    /// </summary>
    [Fact]
    public void TheOutageLineVendorsSayTheyDoNotKnowWhoSolves()
    {
        foreach (var vendor in new[] { "kasada", "akamai" })
        {
            var row = VendorWiring.Rows.Single(r => r.Vendor == vendor);
            Assert.Equal(VendorWiring.Solver.Unknown, row.Solver);
            Assert.False(row.Relayed);
        }
    }

    /// <summary>The remaining two are in-process, and Imperva is not solved at all.</summary>
    [Fact]
    public void TheRestAreLocalOrNone()
    {
        var local = VendorWiring.Rows.Where(r => r.Solver == VendorWiring.Solver.Local).Select(r => r.Vendor).ToList();
        var none = VendorWiring.Rows.Where(r => r.Solver == VendorWiring.Solver.None).Select(r => r.Vendor).ToList();

        // R1052: the two appended rows are Local too, in row order.
        Assert.Equal(new[] { "perimeterx", "queue-it", "botdeflector", "vercel" }, local);
        Assert.Equal(new[] { "imperva" }, none);
    }

    /// <summary>
    /// The axes are independent, which is the whole reason for splitting them: two vendors relay and they do not share a
    /// solver, and two vendors share a solver without sharing the relaying.
    /// </summary>
    [Fact]
    public void TheTwoAxesAreIndependent()
    {
        var relayed = VendorWiring.Rows.Where(r => r.Relayed).Select(r => r.Solver).Distinct().ToList();
        Assert.True(relayed.Count > 1, "relaying should span more than one solver kind");

        var localNotRelayed = VendorWiring.Rows.Count(r => r.Solver == VendorWiring.Solver.Local && !r.Relayed);
        // R1052: four, because botdeflector and vercel are Local and not relayed.
        Assert.Equal(4, localNotRelayed);
    }

    /// <summary>No row silently becomes Unknown where a real answer exists: exactly two do, and they are the outage pair.</summary>
    [Fact]
    public void UnknownIsUsedByExactlyTheOutagePair()
    {
        var unknown = VendorWiring.Rows.Where(r => r.Solver == VendorWiring.Solver.Unknown).Select(r => r.Vendor).ToList();
        Assert.Equal(new[] { "kasada", "akamai" }, unknown);
    }
}
