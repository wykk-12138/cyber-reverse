using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// What a task actually does, as a separate axis from which store it runs against.
///
/// <para>
/// R880. The image's top layer is task kind by store, not store alone, and until now the replica had no counterpart to
/// the first half: <c>Registry.cs</c> has sixty-four store modules and nothing named a kind. R857 established the
/// shape from five entries found in one code region; R879 counted the whole inventory at fourteen flows plus two
/// tasks, and this file is that inventory written down.
/// </para>
///
/// <para>
/// Every member here is an observation, not a guess. The names come from
/// <c>replica/docs/baseline/recovered_async_methods.txt</c>, the 1547-name inventory of the image's async methods,
/// where each appears exactly once as a <c>Start*Flow</c> or <c>Start*Task</c> entry. Nothing is added for symmetry
/// and nothing is inferred from a neighbour: R876's mistake was attributing a sequence to the nearest name, and R878
/// refuted it with arithmetic. The rule adopted here is that a member exists only if a baseline line names it.
/// </para>
///
/// <para>
/// What this type does <b>not</b> claim is behaviour. Knowing that <c>StartRaffleFlow</c> exists says nothing about
/// what a raffle flow does; that is each flow's own work. The type's job is to make the axis countable, so the coverage
/// question "how many kinds does the replica run, and for which stores" has an answer that can be recomputed rather
/// than estimated.
/// </para>
/// </summary>
public enum FlowKind
{
    /// <summary><c>StartNormalFlow</c> — the ordinary checkout.</summary>
    Normal = 0,

    /// <summary><c>StartClearFlow</c> — clearing rather than ordering.</summary>
    Clear = 1,

    /// <summary><c>StartSignupFlow</c> — account signup.</summary>
    Signup = 2,

    /// <summary><c>StartAccountRegistrationFlow</c>. R879 attributes the twelve-step sequence at ordinals 21–34 to
    /// this kind by meaning, since its steps are CheckVerification, SubmitSaleRegistration, Register and
    /// CompleteRegistration. That attribution remains inference.</summary>
    AccountRegistration = 3,

    /// <summary><c>StartPopNowFlow</c> — Pop Mart's immediate-purchase wave.</summary>
    PopNow = 4,

    /// <summary><c>StartInStoreFlow</c> — in-store reservation.</summary>
    InStore = 5,

    /// <summary><c>StartDrawFlow</c>.</summary>
    Draw = 6,

    /// <summary><c>StartDrawCheckFlow</c>.</summary>
    DrawCheck = 7,

    /// <summary><c>StartDrawEventFlow</c>.</summary>
    DrawEvent = 8,

    /// <summary><c>StartExhibitFlow</c>.</summary>
    Exhibit = 9,

    /// <summary><c>StartRaffleFlow</c>.</summary>
    Raffle = 10,

    /// <summary><c>StartReservationFlow</c>.</summary>
    Reservation = 11,

    /// <summary><c>StartRpcFlow</c> — the rpc prefix also appears on model fields such as <c>_rpcFingerprint</c> and
    /// <c>_rpcAdyenPayId</c>, which R876 found in the checkout context model. Whether this kind is "remote procedure
    /// call" or something narrower is unknown; the name is all the evidence there is.</summary>
    Rpc = 12,

    /// <summary><c>StartTasksFlow</c> — a flow whose subject is tasks rather than a store basket.</summary>
    Tasks = 13,
}

/// <summary>
/// The two kinds the image names with <c>Start*Task</c> rather than <c>Start*Flow</c>.
///
/// <para>
/// R880 keeps these separate rather than merging them into <see cref="FlowKind"/> because the image's own names
/// distinguish them: a flow runs a checkout-shaped sequence, a task runs one thing on a schedule. Collapsing the two
/// would be the same error as treating <c>StoreOfflineDraw</c> and <c>drawScratch</c> as one endpoint family — which
/// R877 resolved by finding they serve different things.
/// </para>
/// </summary>
public enum TaskKind
{
    /// <summary><c>StartDailyCheckInTask</c>.</summary>
    DailyCheckIn = 0,

    /// <summary><c>StartPopNowViewTask</c> — viewing rather than buying, so distinct from <see cref="FlowKind.PopNow"/>.</summary>
    PopNowView = 1,
}

/// <summary>
/// The inventory itself, so the counts are recomputable from code rather than from prose.
/// </summary>
public static class TaskKindCatalog
{
    /// <summary>
    /// Each kind against the image name it came from. A kind missing from this map has no evidence and must not be
    /// added to <see cref="FlowKind"/>.
    /// </summary>
    private static readonly IReadOnlyDictionary<FlowKind, string> FlowNames =
        new Dictionary<FlowKind, string>
        {
            [FlowKind.Normal] = "StartNormalFlow",
            [FlowKind.Clear] = "StartClearFlow",
            [FlowKind.Signup] = "StartSignupFlow",
            [FlowKind.AccountRegistration] = "StartAccountRegistrationFlow",
            [FlowKind.PopNow] = "StartPopNowFlow",
            [FlowKind.InStore] = "StartInStoreFlow",
            [FlowKind.Draw] = "StartDrawFlow",
            [FlowKind.DrawCheck] = "StartDrawCheckFlow",
            [FlowKind.DrawEvent] = "StartDrawEventFlow",
            [FlowKind.Exhibit] = "StartExhibitFlow",
            [FlowKind.Raffle] = "StartRaffleFlow",
            [FlowKind.Reservation] = "StartReservationFlow",
            [FlowKind.Rpc] = "StartRpcFlow",
            [FlowKind.Tasks] = "StartTasksFlow",
        };

    private static readonly IReadOnlyDictionary<TaskKind, string> TaskNames =
        new Dictionary<TaskKind, string>
        {
            [TaskKind.DailyCheckIn] = "StartDailyCheckInTask",
            [TaskKind.PopNowView] = "StartPopNowViewTask",
        };

    /// <summary>Every flow kind, in declaration order.</summary>
    public static IReadOnlyList<FlowKind> FlowKinds { get; } =
        FlowNames.Keys.OrderBy(k => (int)k).ToArray();

    /// <summary>Every task kind, in declaration order.</summary>
    public static IReadOnlyList<TaskKind> TaskKinds { get; } =
        TaskNames.Keys.OrderBy(k => (int)k).ToArray();

    /// <summary>The image's name for a flow kind, or null when the kind has no evidence — which should never happen.</summary>
    public static string? ImageName(FlowKind kind) =>
        FlowNames.TryGetValue(kind, out var n) ? n : null;

    /// <summary>The image's name for a task kind.</summary>
    public static string? ImageName(TaskKind kind) =>
        TaskNames.TryGetValue(kind, out var n) ? n : null;

    /// <summary>
    /// Resolves a <c>Start*Flow</c> or <c>Start*Task</c> name back to what it denotes. Returns null for a name this
    /// catalog does not claim, which is the honest answer to "is this kind covered".
    /// </summary>
    public static (FlowKind? Flow, TaskKind? Task) Resolve(string imageName)
    {
        foreach (var kv in FlowNames)
            if (kv.Value == imageName) return (kv.Key, null);
        foreach (var kv in TaskNames)
            if (kv.Value == imageName) return (null, kv.Key);
        return (null, null);
    }
}
