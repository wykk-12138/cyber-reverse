using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 122: the R121 ruler applied to every flow — and the honest answer that most flows have no
/// ownership witness.
///
/// <para>
/// A lambda literal proves ownership only when its ordinals match the flow's own. Two flows qualify
/// (John Lewis 20–39, Nike 41–58); six do not. So Pop Mart's 121–130 gap stays unresolved, and the
/// candidates from R120 stay candidates — which is the point of having a rule instead of a habit.
/// </para>
///
/// <para>
/// The scan's side effect is a real find: a six-method cart class whose names match Pop Mart's
/// <c>/shop/v1/*</c> family, i.e. the <b>buying</b> half of a store whose draw half has twenty-four
/// steps.
/// </para>
/// </summary>
public sealed class LambdaWitnessTests
{
    private readonly ITestOutputHelper _out;

    public LambdaWitnessTests(ITestOutputHelper output) => _out = output;

    /// <summary>Two flows witnessed, six not, eight examined.</summary>
    [Fact]
    public void MostFlowsHaveNoWitness()
    {
        Assert.Equal(2, LambdaWitness.Witnessed.Count);
        Assert.Equal(6, LambdaWitness.Unwitnessed.Count);
        Assert.Equal(8, LambdaWitness.ExaminedCount);

        foreach (var (flow, range) in LambdaWitness.Witnessed)
            _out.WriteLine($"witnessed: {flow} ({range.From}..{range.To})");
        foreach (var flow in LambdaWitness.Unwitnessed)
            _out.WriteLine($"no witness: {flow}");
    }

    /// <summary>The witness ranges match the flows' own ordinals.</summary>
    [Fact]
    public void TheWitnessRangesMatchTheFlows()
    {
        var (jlFrom, jlTo) = LambdaWitness.Witnessed["johnlewis"];
        Assert.Equal(StoreFlowSteps.JohnLewis.Steps.Min(s => s.Ordinal), jlFrom);
        Assert.Equal(StoreFlowSteps.JohnLewis.Steps.Max(s => s.Ordinal), jlTo);

        var (nikeFrom, nikeTo) = LambdaWitness.Witnessed["nike"];
        Assert.Equal(StoreFlowSteps.Nike.Steps.Min(s => s.Ordinal), nikeFrom);
        Assert.Equal(StoreFlowSteps.Nike.Steps.Max(s => s.Ordinal), nikeTo);
    }

    /// <summary>Pop Mart has no witness — its gap stays unresolved and its candidates stay candidates.</summary>
    [Fact]
    public void PopMartHasNoWitnessSoItsCandidatesStayCandidates()
    {
        Assert.False(LambdaWitness.HasWitness("popmart"));
        Assert.Contains("popmart", LambdaWitness.Unwitnessed);

        foreach (var candidate in CandidateSteps.All)
            Assert.True(CandidateSteps.IsCandidate(candidate.Name));

        Assert.False(LambdaWitness.HasWitness(null));
        Assert.True(LambdaWitness.HasWitness("nike"));
    }

    /// <summary>
    /// Names repeat across classes, which is why a literal mentioning three of a flow's steps can
    /// still belong to something else.
    /// </summary>
    [Fact]
    public void NamesRepeatAcrossClasses()
    {
        Assert.Contains("repeat across classes", LambdaWitness.Duplication);
        Assert.Contains("unless its ordinals match", LambdaWitness.Duplication);

        // the example the scan produced: Authorize at ordinal 1, not Nike's 42
        Assert.True(StoreFlowSteps.IsStep("Authorize"));
        Assert.Equal(42, StoreFlowSteps.Nike.Steps.First(s => s.Name == "Authorize").Ordinal);

        _out.WriteLine(LambdaWitness.Duplication);
    }

    /// <summary>Pop Mart's cart class: six methods, five distinct names.</summary>
    [Fact]
    public void ThePopMartCartClassHasSixMethods()
    {
        Assert.Equal(6, PopMartCartSteps.All.Count);
        Assert.Equal(5, PopMartCartSteps.DistinctNames.Count);

        // the duplicate is an overload, kept as two entries
        Assert.Equal(2, PopMartCartSteps.Names.Count(n => n == "FetchAddress"));

        foreach (var step in PopMartCartSteps.All) _out.WriteLine($"{step.Ordinal}: {step.Name}");
    }

    /// <summary>The cart class lines up with endpoints the family already carries.</summary>
    [Fact]
    public void TheCartClassMatchesTheEndpointFamily()
    {
        Assert.True(PopMartCartSteps.IsMember("GetCartDataList"));
        Assert.True(PopMartCartSteps.IsMember("FetchCoupons"));
        Assert.True(PopMartCartSteps.IsMember("SubmitDiscount"));
        Assert.True(PopMartCartSteps.IsMember("ClearCart"));

        Assert.False(PopMartCartSteps.IsMember("EnterDraw"));
        Assert.False(PopMartCartSteps.IsMember(null));

        // the endpoints exist in the family this session already recorded
        Assert.True(PopMartEndpoints.IsKnown(PopMartEndpoints.ShoppingCartDataList));
        Assert.True(PopMartEndpoints.IsKnown(PopMartEndpoints.CouponsList));

        _out.WriteLine("draw class = 24 steps; cart class = 6 methods; two halves of one store");
    }
}
