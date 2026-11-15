using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Who has an ownership witness, and who does not — the ruler from R121 applied to every flow in R122.
///
/// <para>
/// The rule is narrow, and applying it widely shows how narrow: a lambda literal proves ownership only
/// when its <b>ordinals line up with the flow's own ordinals</b>. John Lewis has that (methods 20–39,
/// names attached) and Nike has it (41–58). Pop Mart does not: no lambda literal anywhere carries
/// ordinals in its 104–153 range, so its 121–130 gap has <b>no witness</b> and its candidates stay
/// candidates.
/// </para>
///
/// <para>
/// The scan also produced a genuine find of a different kind. A cart class exists with six methods in
/// plain order — <c>GetCartDataList 1</c>, <c>FetchCoupons 2</c>, <c>SubmitDiscount 3</c>,
/// <c>ClearCart 4</c>, <c>FetchAddress 5</c> and 6 — whose names match Pop Mart's
/// <c>/shop/v1/*</c> family exactly (<c>cartDataList</c>, <c>couponsList</c>, coupon submit, address
/// fetch). That is Pop Mart's <b>other half</b>: the draw class has twenty-four steps and this class
/// does the buying.
/// </para>
/// </summary>
public static class LambdaWitness
{
    /// <summary>Flows whose lambda literal carries the flow's own ordinals, and the range it covers.</summary>
    public static readonly IReadOnlyDictionary<string, (int From, int To)> Witnessed =
        new Dictionary<string, (int, int)>(System.StringComparer.Ordinal)
        {
            ["johnlewis"] = (20, 39),
            ["nike"] = (41, 58),
        };

    /// <summary>Flows with no ownership witness — their gaps stay unresolved.</summary>
    public static readonly IReadOnlyList<string> Unwitnessed = new[]
    {
        "popmart", "demandware-classic", "demandware-dual", "collectplus-app",
        "structure-token-multi", "structure-token-single",
    };

    /// <summary>
    /// Names repeated across classes, which is why a bare name proves nothing on its own: a lambda
    /// literal for a <i>different</i> class can mention three of a flow's step names and still not be
    /// that flow's table. <c>Authorize</c> at ordinal 1 is the example R122 found.
    /// </summary>
    public const string Duplication =
        "step names repeat across classes; a literal mentioning them is not the flow's table " +
        "unless its ordinals match the flow's";

    /// <summary>True when the flow has an ownership witness for its own ordinals.</summary>
    public static bool HasWitness(string? flow) =>
        !string.IsNullOrEmpty(flow) && Witnessed.ContainsKey(flow);

    /// <summary>Total flows examined.</summary>
    public static int ExaminedCount => Witnessed.Count + Unwitnessed.Count;
}

/// <summary>
/// Pop Mart's cart class — six methods in plain order, found in R122 by the same scan that failed to
/// witness the draw class.
///
/// <code>
/// 1 GetCartDataList   2 FetchCoupons   3 SubmitDiscount
/// 4 ClearCart         5 FetchAddress  6 FetchAddress   (two ordinals, one name)
/// </code>
///
/// <para>
/// The names line up with endpoints the family already carries — <c>cartDataList</c>,
/// <c>couponsList</c>, coupon submit, address fetch — which is why this class is recorded as the
/// <b>buying</b> half of Pop Mart while <see cref="StoreFlowSteps.PopMart"/> is the draw half.
/// The duplicate <c>FetchAddress</c> at two ordinals is kept as two entries: two methods with one name
/// is an overload, and collapsing them would hide a method.
/// </para>
/// </summary>
public static class PopMartCartSteps
{
    /// <summary>One method: name and ordinal.</summary>
    public sealed record Step(string Name, int Ordinal);

    public static readonly IReadOnlyList<Step> All = new[]
    {
        new Step("GetCartDataList", 1),
        new Step("FetchCoupons", 2),
        new Step("SubmitDiscount", 3),
        new Step("ClearCart", 4),
        new Step("FetchAddress", 5),
        new Step("FetchAddress", 6),
    };

    /// <summary>Names, including the overload twice.</summary>
    public static IReadOnlyList<string> Names => All.Select(s => s.Name).ToList();

    /// <summary>Distinct names — five, because <c>FetchAddress</c> is an overload.</summary>
    public static IReadOnlyList<string> DistinctNames => Names.Distinct().ToList();

    /// <summary>True when the name is a method of this class.</summary>
    public static bool IsMember(string? name) =>
        !string.IsNullOrEmpty(name) && Names.Contains(name);
}
