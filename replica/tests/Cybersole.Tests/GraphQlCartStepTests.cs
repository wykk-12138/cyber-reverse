using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 121: the GraphQL cart class, and the rule that finally settles ownership.
///
/// <para>
/// R120 left <c>AddToCartGraphQL</c> as a candidate because a bare ordinal cannot say which class owns
/// a name. This round found the witness: the class's <b>lambda literal</b>, emitted as a single string
/// that lists five consecutive method numbers with their names. That is one class's own method list.
/// </para>
///
/// <para>
/// The contrast is the point. The <c>d__</c> run reads
/// <c>1046:GetAccessToken 1050:CartApiObjectCreate 106:AddToCartGraphQL</c> — ordinals 1046 and 1050
/// belong to a much larger class whose strings merely sit beside this one in the pool. <b>Pool
/// adjacency is adjacency in the file, not membership in a class.</b>
/// </para>
/// </summary>
public sealed class GraphQlCartStepTests
{
    private readonly ITestOutputHelper _out;

    public GraphQlCartStepTests(ITestOutputHelper output) => _out = output;

    /// <summary>Six members, ordered, distinct.</summary>
    [Fact]
    public void TheClassHasSixMembers()
    {
        foreach (var step in GraphQlCartSteps.All) _out.WriteLine($"d__{step.Ordinal,-4} {step.Name}");

        Assert.Equal(6, GraphQlCartSteps.All.Count);
        Assert.Equal(6, GraphQlCartSteps.Names.Distinct().Count());

        var ordinals = GraphQlCartSteps.All.Select(s => s.Ordinal).ToList();
        Assert.Equal(ordinals.OrderBy(o => o), ordinals);
    }

    /// <summary>Four of the six are GraphQL cart calls — the half R96 found missing.</summary>
    [Fact]
    public void FourOfThemAreGraphQlCartCalls()
    {
        Assert.Equal(4, GraphQlCartSteps.GraphQlCalls.Count);
        Assert.All(GraphQlCartSteps.GraphQlCalls, s => Assert.Contains("Graphql", s.Name,
            System.StringComparison.OrdinalIgnoreCase));

        foreach (var call in GraphQlCartSteps.GraphQlCalls) _out.WriteLine("graphql: " + call.Name);
    }

    /// <summary>
    /// The four were candidates in R120 and are members now — the promotion is evidence-backed, so the
    /// two lists are allowed to overlap for exactly these names.
    /// </summary>
    [Fact]
    public void TheGraphQlNamesGraduatedFromCandidates()
    {
        foreach (var call in GraphQlCartSteps.GraphQlCalls)
        {
            Assert.True(CandidateSteps.IsCandidate(call.Name), call.Name);
            Assert.True(GraphQlCartSteps.IsMember(call.Name), call.Name);

            // the candidate record and the member record agree on the ordinal
            Assert.Equal(GraphQlCartSteps.OrdinalOf(call.Name), CandidateSteps.For(call.Name)!.Ordinal);
        }

        // and they are still not steps of a store flow — this is a different class
        Assert.All(GraphQlCartSteps.GraphQlCalls,
            c => Assert.False(StoreFlowSteps.IsStep(c.Name)));

        _out.WriteLine("promoted from candidate to class member, not to a store-flow step");
    }

    /// <summary>The witness and the rule are recorded, and the rule names both sides.</summary>
    [Fact]
    public void TheWitnessAndTheRuleAreRecorded()
    {
        Assert.Contains("one lambda literal", GraphQlCartSteps.OwnershipWitness);
        Assert.Contains("105..109", GraphQlCartSteps.OwnershipWitness);

        Assert.Contains("lambda literal is the ownership witness", GraphQlCartSteps.Rule);
        Assert.Contains("d__ run is not", GraphQlCartSteps.Rule);
        Assert.Contains("pool adjacency is not", GraphQlCartSteps.Rule,
            System.StringComparison.OrdinalIgnoreCase);

        _out.WriteLine(GraphQlCartSteps.Rule);
    }

    /// <summary>Membership is exact.</summary>
    [Fact]
    public void MembershipIsExact()
    {
        Assert.True(GraphQlCartSteps.IsMember("AddToCartGraphQL"));
        Assert.True(GraphQlCartSteps.IsMember("RefreshEmailLogin"));
        Assert.False(GraphQlCartSteps.IsMember("GetAccessToken"));   // the 1046 one, another class
        Assert.False(GraphQlCartSteps.IsMember(null));

        Assert.Equal(109, GraphQlCartSteps.OrdinalOf("GetCartAvailabilityGraphql"));
        Assert.Null(GraphQlCartSteps.OrdinalOf("Nope"));
    }
}
