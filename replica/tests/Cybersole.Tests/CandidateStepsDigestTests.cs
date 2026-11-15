using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R295: the nine candidates are real — every one of them exists in the image as a <c>d__N</c> state machine, and every
/// name they cite as a collision exists too (checked against the pool in R295; the earlier "not in pool" reading was my
/// own regex looking for a bare name instead of <c>&lt;Name&gt;d__N</c>).
///
/// <para>
/// They are still only candidates: ordinals are per class, so a name seen at an ordinal may belong to another class.
/// This table pins what the replica claims so the list cannot drift, and pins the caveat so it cannot be dropped.
/// </para>
/// </summary>
public sealed class CandidateStepsDigestTests
{
    private readonly ITestOutputHelper _out;
    public CandidateStepsDigestTests(ITestOutputHelper output) => _out = output;

    private static readonly (string Name, int Ordinal)[] Expected =
    {
        ("AddToCartGraphQL", 106),
        ("AddToCartPreloadGraphQL", 107),
        ("CreateCartGraphql", 108),
        ("GetCartAvailabilityGraphql", 109),
        ("CompletePayPalPayment", 125),
        ("CompletePayPalGuestPayment", 126),
        ("CompleteForwardPayment", 127),
        ("AddToCartStoreFront", 128),
        ("AddToCartPreload", 130),
    };

    [Fact]
    public void TheNineCandidatesAndTheirOrdinalsArePinned()
    {
        var actual = CandidateSteps.All.Select(c => (c.Name, c.Ordinal)).ToList();
        foreach (var c in actual) _out.WriteLine($"{c.Name}: {c.Ordinal}");

        Assert.Equal(Expected, actual);
    }

    [Fact]
    public void EveryCandidateIsStillOnlyACandidate()
    {
        // none of these may appear in a flow: they are ordinal-scan findings, not proven steps
        var flowNames = StoreFlowSteps.All.SelectMany(f => f.Names).ToHashSet();
        foreach (var candidate in CandidateSteps.All)
        {
            _out.WriteLine($"{candidate.Name}: in a flow = {flowNames.Contains(candidate.Name)}");
            Assert.DoesNotContain(candidate.Name, flowNames);
        }
    }

    [Fact]
    public void TheCaveatIsStillWrittenDown()
    {
        Assert.Contains("ownership unproven", CandidateSteps.Evidence);
        Assert.Contains("not merged into StoreFlowSteps", CandidateSteps.Evidence);
    }
}
