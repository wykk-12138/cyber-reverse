using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 120: candidate steps — and why an ordinal scan cannot promote a name to a step.
///
/// <para>
/// R119 learned to read a class's <b>lambda literal</b> when its step run skips an ordinal. R120 tried
/// the cheaper route: scan every literal for <c>&lt;Name&gt;d__N</c> and group by ordinal. It finds
/// real names — <c>AddToCartGraphQL</c>, <c>CreateCartGraphql</c>, <c>CompletePayPalPayment</c>,
/// <c>AddToCartStoreFront</c> — but it cannot say which class they belong to, because
/// <b>ordinals are per class</b>: ordinal 126 carries three different classes' methods at once.
/// </para>
///
/// <para>
/// So the scan's output is a candidate list, kept separate from <see cref="StoreFlowSteps"/> and
/// labelled. Two families in it are worth chasing properly: the GraphQL cart steps (106–109) agree
/// with R101's persisted operations, and the PayPal steps (125–127) agree with R118's finding that
/// one store reaches its payment provider directly.
/// </para>
/// </summary>
public sealed class CandidateStepTests
{
    private readonly ITestOutputHelper _out;

    public CandidateStepTests(ITestOutputHelper output) => _out = output;

    /// <summary>Nine candidates across three families.</summary>
    [Fact]
    public void TheScanProducedNineCandidates()
    {
        Assert.Equal(9, CandidateSteps.All.Count);
        Assert.Equal(4, CandidateSteps.GraphQlCart.Count);
        Assert.Equal(3, CandidateSteps.PaymentCompletion.Count);
        Assert.Equal(2, CandidateSteps.StorefrontCart.Count);

        foreach (var c in CandidateSteps.All)
            _out.WriteLine($"d__{c.Ordinal,-4} {c.Name,-28} shares with: {c.Collision}");
    }

    /// <summary>
    /// At least one ordinal carries three classes' methods — the reason the scan cannot be trusted
    /// on its own.
    /// </summary>
    [Fact]
    public void OrdinalCollisionsAreRecordedOnEveryCollidingCandidate()
    {
        var colliding = CandidateSteps.All.Where(c => c.Collision != "none").ToList();

        _out.WriteLine($"{colliding.Count} of {CandidateSteps.All.Count} carry a collision");
        Assert.True(colliding.Count >= 5);

        var threeWay = CandidateSteps.For("CompletePayPalGuestPayment");
        Assert.NotNull(threeWay);
        Assert.Contains("Register", threeWay!.Collision);
        Assert.Contains("SubmitKlaviyoSubscription", threeWay.Collision);
    }

    /// <summary>
    /// No candidate is a confirmed step of any flow — the two lists stay separate.
    /// </summary>
    [Fact]
    public void NoCandidateWasPromotedToAStep()
    {
        foreach (var c in CandidateSteps.All)
        {
            Assert.True(CandidateSteps.IsCandidate(c.Name));
            Assert.False(StoreFlowSteps.IsStep(c.Name), c.Name + " was promoted without evidence");
        }

        _out.WriteLine("candidate list and step list are disjoint");
    }

    /// <summary>The GraphQL cart family is the one that agrees with an earlier finding.</summary>
    [Fact]
    public void TheGraphQlCartFamilyAgreesWithThePersistedOperations()
    {
        var names = CandidateSteps.GraphQlCart.Select(c => c.Name).ToList();

        Assert.Contains("AddToCartGraphQL", names);
        Assert.Contains("CreateCartGraphql", names);
        Assert.Contains("GetCartAvailabilityGraphql", names);

        // R101 recorded six persisted operations; this family is the cart half of the same design
        Assert.Equal(6, NikePersistedOperations.All.Count);
        _out.WriteLine($"{names.Count} GraphQL cart candidates vs 6 persisted operations");
    }

    /// <summary>The caveat is in the data, and asserted here.</summary>
    [Fact]
    public void TheCaveatIsRecorded()
    {
        Assert.Contains("ordinals are per class", CandidateSteps.Evidence);
        Assert.Contains("ownership unproven", CandidateSteps.Evidence);
        Assert.Contains("not merged", CandidateSteps.Evidence);

        Assert.Null(CandidateSteps.For("NotACandidate"));
        Assert.Null(CandidateSteps.For(null));
    }
}
