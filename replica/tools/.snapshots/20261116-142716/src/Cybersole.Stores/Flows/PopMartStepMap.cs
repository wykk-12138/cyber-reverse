using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Pop Mart's twenty-four steps against its thirty-nine <c>/shop/v1/*</c> endpoints, paired in R116
/// where the nouns agree.
///
/// <para>
/// This is the same discipline as the Scheels map in R115: a <b>name correlation</b>, not a capture.
/// The two lists are the largest pair in the image (24 steps, 39 endpoints), so the gaps are recorded
/// as carefully as the matches — <see cref="UnmappedSteps"/> and <see cref="UnmappedEndpoints"/> are
/// first-class data, not omissions.
/// </para>
///
/// <para>
/// Where the match is exact the pair is obvious: <c>EnterDraw</c> ↔ <c>DrawScratchDraw</c>,
/// <c>ChooseGoods</c> ↔ <c>DrawScratchChooseGoods</c>, <c>RedeemLuckPoints</c> ↔
/// <c>LuckyPointsDraw</c>, <c>FindDates</c> ↔ <c>StoreTicketDates</c>. Where it is a guess the step is
/// left unmapped: <c>CheckResult</c> could be <c>DrawScratchDetail</c> or a poll of the same call, and
/// nothing in the image says which.
/// </para>
/// </summary>
public static class PopMartStepMap
{
    /// <summary>Step name → endpoint, where the two names agree on the noun.</summary>
    public static readonly IReadOnlyDictionary<string, string> Pairs =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["GetOrders"] = PopMartEndpoints.OrderList,
            ["StartDrawFlow"] = PopMartEndpoints.DrawScratchDetail,
            ["FindDraw"] = PopMartEndpoints.DrawScratchDetail,
            ["EnterDraw"] = PopMartEndpoints.DrawScratchDraw,
            ["ChooseGoods"] = PopMartEndpoints.DrawScratchChooseGoods,
            ["FindMegaDraw"] = PopMartEndpoints.MegaDrawHit,
            ["EnterDrawEvent"] = PopMartEndpoints.MegaDrawHit,
            ["RedeemMemberPoints"] = PopMartEndpoints.PointsRedeemDraw,
            ["RedeemLuckPoints"] = PopMartEndpoints.LuckyPointsDraw,
            ["FindExhibit"] = PopMartEndpoints.StoreOfflineDrawInfo,
            ["EnterExhibit"] = PopMartEndpoints.StoreOfflineDrawJoin,
            ["FindDates"] = PopMartEndpoints.StoreTicketDates,
            ["FindTimeSlots"] = PopMartEndpoints.StoreTicketMainPage,
            ["EnterReservation"] = PopMartEndpoints.StoreOfflineDrawJoin,
        };

    /// <summary>Steps with no endpoint whose name agrees — the honest remainder.</summary>
    public static readonly IReadOnlyList<string> UnmappedSteps =
        StoreFlowSteps.PopMart.Names.Where(n => !Pairs.ContainsKey(n)).ToList();

    /// <summary>Endpoints no step names — the honest remainder on the other side.</summary>
    public static readonly IReadOnlyList<string> UnmappedEndpoints =
        PopMartEndpoints.All.Where(e => !Pairs.Values.Contains(e)).ToList();

    /// <summary>
    /// How this map was drawn. Asserted by a test so the label cannot be quietly dropped.
    /// </summary>
    public const string Evidence =
        "name correlation between the 24 Pop Mart steps and the 39 /shop/v1 endpoints; " +
        "no request capture; unmapped steps and endpoints are recorded, not guessed";

    /// <summary>The endpoint a step pairs with, or null when the names do not agree.</summary>
    public static string? EndpointFor(string? step) =>
        string.IsNullOrEmpty(step) ? null
            : Pairs.TryGetValue(step, out var endpoint) ? endpoint : null;

    /// <summary>The steps that pair with an endpoint, in flow order.</summary>
    public static IReadOnlyList<string> MappedSteps =>
        StoreFlowSteps.PopMart.Names.Where(Pairs.ContainsKey).ToList();
}
