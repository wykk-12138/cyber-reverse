using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1027: R1026's single RemoteApi value was covering two different arrangements, and the second is not the first.
///
/// <para>
/// R1026 reasoned from "the failure vocabulary includes API down (Contact staff)" to "this vendor is solved remotely",
/// and found exactly Kasada and Akamai. That is a real signal and it is not the only kind of remote solving: the image
/// also runs services of its own, named cf-solver.cybersole.io with a /v1/warm endpoint, cloudflare-jsd-gen on the
/// Worker, and datadome.cybersole.io/sensor. Cloudflare and DataDome use those and carry no outage line, because an
/// outage line is what you write when somebody else's API can fail.
/// </para>
///
/// <para>
/// So the column splits. Relay means the original routes through a service it owns. ThirdPartyApi means it calls one it
/// does not, and is the only case where "API down, contact staff" makes sense. A vendor with neither is Local.
/// </para>
/// </summary>
public sealed class VendorSolvingModeTests
{
    /// <summary>The two with an outage line call somebody else, and they are the only ones.</summary>
    [Fact]
    public void OnlyTheTwoWithAnOutageLineCallAThirdParty()
    {
        // Row order, not alphabetical -- this repository has caught me on that three times.
        var thirdParty = VendorWiring.Rows
            .Where(r => r.How == VendorWiring.How.ThirdPartyApi)
            .Select(r => r.Vendor)
            .ToList();

        Assert.Equal(new[] { "kasada", "akamai" }, thirdParty);
    }

    /// <summary>
    /// The two with a host under cybersole.io or on the Worker go through the original's own service.
    /// </summary>
    [Fact]
    public void TheTwoWithARelayHostUseIt()
    {
        var relay = VendorWiring.Rows
            .Where(r => r.How == VendorWiring.How.Relay)
            .Select(r => r.Vendor)
            .ToList();

        Assert.Equal(new[] { "cloudflare", "datadome" }, relay);
    }

    /// <summary>The rest are solved in-process, and imperva is not solved at all.</summary>
    [Fact]
    public void TheRestAreLocalOrNone()
    {
        var local = VendorWiring.Rows.Where(r => r.How == VendorWiring.How.Local).Select(r => r.Vendor).ToList();
        var none = VendorWiring.Rows.Where(r => r.How == VendorWiring.How.None).Select(r => r.Vendor).ToList();

        Assert.Equal(new[] { "perimeterx", "queue-it" }, local);
        Assert.Equal(new[] { "imperva" }, none);
    }

    /// <summary>
    /// No row has both a relay host and an outage line, which is the observation that forced the split: the two signals
    /// never co-occur, so one column could not honestly hold both.
    /// </summary>
    [Fact]
    public void RelayAndThirdPartyAreDisjoint()
    {
        Assert.DoesNotContain(VendorWiring.Rows,
            r => r.How == VendorWiring.How.Relay && r.Note.Contains("API down"));
    }

    /// <summary>Unknown exists for a future row that cannot tell; nothing claims it yet.</summary>
    [Fact]
    public void NoRowClaimsUnknownYet()
    {
        Assert.DoesNotContain(VendorWiring.Rows, r => r.How == VendorWiring.How.Unknown);
    }

    /// <summary>The column carries information only if more than one value is in use.</summary>
    [Fact]
    public void TheColumnDistinguishesTheCases()
    {
        var kinds = VendorWiring.Rows.Select(r => r.How).Distinct().Count();
        Assert.True(kinds >= 4, "expected at least four distinct solving modes among seven rows, saw " + kinds);
    }
}
