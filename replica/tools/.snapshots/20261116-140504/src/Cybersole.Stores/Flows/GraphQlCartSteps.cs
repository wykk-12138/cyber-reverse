using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The GraphQL cart class, confirmed in R121 — and the round that settled <b>which evidence proves
/// ownership</b>.
///
/// <para>
/// R120 recorded <c>AddToCartGraphQL</c> and friends as candidates because ordinals are per class.
/// This round found the witness that does settle it: the class's <b>lambda literal</b>, which the
/// compiler emits as one string listing every method that has a lambda:
/// </para>
///
/// <code>
/// :&lt;CartApiObjectCreate&gt;b__105_0 4&lt;AddToCartGraphQL&gt;b__106_0 B&lt;AddToCartPreloadGraphQL&gt;b__107_0
/// 6&lt;CreateCartGraphql&gt;b__108_0 H&lt;GetCartAvailabilityGraphql&gt;b__109_0 …
/// </code>
///
/// <para>
/// Five consecutive method numbers with their names attached, in one string — that is one class's own
/// method list. Compare the <c>d__</c> run, which reads
/// <c>1046:GetAccessToken 1050:CartApiObjectCreate 106:AddToCartGraphQL</c>: ordinals 1046 and 1050
/// belong to a different, much larger class whose strings merely sit next to this one in the pool.
/// </para>
///
/// <para>
/// <b>So the rule this session has been circling for ten rounds is: the lambda literal is the
/// ownership witness; a <c>d__</c> run is not.</b> Adjacency in the string pool is adjacency in the
/// file, not membership in a class.
/// </para>
/// </summary>
public static class GraphQlCartSteps
{
    /// <summary>One method of the class: name and its own ordinal.</summary>
    public sealed record Step(string Name, int Ordinal);

    /// <summary>
    /// The class's methods, in ordinal order. <c>RefreshEmailLogin</c> at 114 is included because the
    /// same lambda literal names it — it belongs to the class even though it is not a cart call.
    /// </summary>
    public static readonly IReadOnlyList<Step> All = new[]
    {
        new Step("CartApiObjectCreate", 105),
        new Step("AddToCartGraphQL", 106),
        new Step("AddToCartPreloadGraphQL", 107),
        new Step("CreateCartGraphql", 108),
        new Step("GetCartAvailabilityGraphql", 109),
        new Step("RefreshEmailLogin", 114),
    };

    /// <summary>The four GraphQL cart calls — the ones R96 found the replica missing entirely.</summary>
    public static readonly IReadOnlyList<Step> GraphQlCalls = new[]
    {
        new Step("AddToCartGraphQL", 106),
        new Step("AddToCartPreloadGraphQL", 107),
        new Step("CreateCartGraphql", 108),
        new Step("GetCartAvailabilityGraphql", 109),
    };

    /// <summary>Names, in order.</summary>
    public static IReadOnlyList<string> Names => All.Select(s => s.Name).ToList();

    /// <summary>
    /// The witness that proves these belong together, quoted so it cannot drift.
    /// </summary>
    public const string OwnershipWitness =
        "one lambda literal lists 105..109 and 114 with their names — one class's own method list";

    /// <summary>The rule this round established, asserted by a test.</summary>
    public const string Rule =
        "the lambda literal is the ownership witness; a d__ run is not — pool adjacency is not " +
        "class membership";

    /// <summary>True when the name is a method of this class.</summary>
    public static bool IsMember(string? name) =>
        !string.IsNullOrEmpty(name) && All.Any(s => s.Name == name);

    /// <summary>The ordinal of a member, or null.</summary>
    public static int? OrdinalOf(string? name) =>
        string.IsNullOrEmpty(name) ? null : All.FirstOrDefault(s => s.Name == name)?.Ordinal;
}
