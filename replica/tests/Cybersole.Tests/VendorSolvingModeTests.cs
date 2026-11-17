using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1026: the image's outcome vocabulary splits into a detection layer and a solving layer, and reading both gives a
/// fact the audit did not have.
///
/// <para>
/// Detection lines are "&lt;Vendor&gt; Failed", "Blocked", "block", "(Rotating)". Solving lines are
/// "Solving &lt;Vendor&gt; (...)" and "Failed Solving &lt;Vendor&gt; (...)" with a reason attached -- no clearance, too
/// many rounds, TL, SBSD, SDS, Softblock. Only Kasada and Akamai also carry "&lt;Vendor&gt; API down (Contact staff)",
/// and an API can go down while a local routine cannot: it simply fails. So those two are solved through a remote
/// service and the rest in-process.
/// </para>
/// </summary>
public sealed class VendorSolvingModeTests
{
    /// <summary>Exactly two vendors are solved through a service, and they are the two with an outage line.</summary>
    [Fact]
    public void OnlyTheTwoWithAnOutageLineAreRemote()
    {
        var remote = VendorWiring.Rows
            .Where(r => r.How == VendorWiring.How.RemoteApi)
            .Select(r => r.Vendor)
            .ToList();

        // Row order, not alphabetical -- the third time this repository has caught me on that, after R1009 and R1024.
        Assert.Equal(new[] { "kasada", "akamai" }, remote);
    }

    /// <summary>The rest that are solved are solved locally, and imperva is not solved at all.</summary>
    [Fact]
    public void TheOthersSplitBetweenLocalAndNone()
    {
        var local = VendorWiring.Rows
            .Where(r => r.How == VendorWiring.How.Local)
            .Select(r => r.Vendor)
            .ToList();
        var none = VendorWiring.Rows
            .Where(r => r.How == VendorWiring.How.None)
            .Select(r => r.Vendor)
            .ToList();

        Assert.Equal(new[] { "cloudflare", "datadome", "perimeterx", "queue-it" }, local);
        Assert.Equal(new[] { "imperva" }, none);
    }

    /// <summary>
    /// Nothing claims Unknown. That value exists so a future row can say it does not know, and a test that allowed it
    /// to appear silently would defeat the point of having it.
    /// </summary>
    [Fact]
    public void NoRowClaimsUnknownYet()
    {
        Assert.DoesNotContain(VendorWiring.Rows, r => r.How == VendorWiring.How.Unknown);
    }

    /// <summary>
    /// RemoteApi and Local have to disagree about at least one vendor, or the column is not carrying information.
    /// </summary>
    [Fact]
    public void TheColumnDistinguishesTheTwo()
    {
        var remote = VendorWiring.Rows.Count(r => r.How == VendorWiring.How.RemoteApi);
        var local = VendorWiring.Rows.Count(r => r.How == VendorWiring.How.Local);

        Assert.True(remote > 0 && local > 0, "the column must have both values in use");
    }
}
