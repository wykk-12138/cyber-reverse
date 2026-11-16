namespace Cybersole.Core;

/// <summary>
/// How long a group's limits last before they roll over.
///
/// <para>
/// R53: this enum did not exist here, and <c>TaskGroup.UsageExpiry</c> was a <c>DateTime?</c>
/// edited with a date box. The original models it differently. Three XAML bindings in
/// <c>Cybersole.exe</c> name the type:
/// </para>
///
/// <code>
/// Cybersole.Ui.Views.Tasks.Modals.TaskGroupView,Cybersole.TimeSpans!Property
///   → Cybersole.Models.TaskGroup,Cybersole.Core.UsageExpiry!Property
/// Cybersole.Ui.Views.Proxies.Modals.ProxyGroupView,Cybersole.TimeSpans!Property
///   → Cybersole.Models.ProxyGroup,Cybersole.Core.UsageExpiry!Property
/// Cybersole.Ui.Views.SmartActions.SmartActionsCreator,Cybersole.TimeSpans!Property
/// </code>
///
/// <para>
/// So <c>UsageExpiry</c> is a duration choice, not an instant. The locale agrees — the label is
/// "Reset limits <em>after</em>", and the options are durations:
/// <c>TaskGroup.TimeSpan.30Minutes</c>, <c>.1Hour</c>, <c>.3Hour</c>, <c>.6Hour</c>,
/// <c>.12Hour</c>, <c>.1Day</c>, <c>.Manual</c>.
/// </para>
///
/// <para>
/// A separate field holds the computed boundary: <c>TaskGroup.NextReset</c> is getter-only in the
/// original (<c>get_NextReset</c> with no <c>set_</c>), i.e. derived from this and the period
/// start rather than stored.
/// </para>
/// </summary>
public enum TimeSpans
{
    /// <summary><c>TaskGroup.TimeSpan.30Minutes</c></summary>
    ThirtyMinutes,

    /// <summary><c>TaskGroup.TimeSpan.1Hour</c></summary>
    OneHour,

    /// <summary><c>TaskGroup.TimeSpan.3Hour</c></summary>
    ThreeHours,

    /// <summary><c>TaskGroup.TimeSpan.6Hour</c></summary>
    SixHours,

    /// <summary><c>TaskGroup.TimeSpan.12Hour</c></summary>
    TwelveHours,

    /// <summary><c>TaskGroup.TimeSpan.1Day</c></summary>
    OneDay,

    /// <summary>
    /// <c>TaskGroup.TimeSpan.Manual</c> — the user sets the boundary themselves, which is what
    /// <c>TaskGroup.PeriodStart.Tooltip</c> ("Period starts when you first start a task") is
    /// describing as the alternative.
    /// </summary>
    Manual,
}

/// <summary>Durations for <see cref="TimeSpans"/>.</summary>
public static class TimeSpansExtensions
{
    /// <summary>
    /// The length of one period, or <c>null</c> for <see cref="TimeSpans.Manual"/> — manual means
    /// "no fixed period", so there is nothing to add.
    /// </summary>
    public static TimeSpan? ToDuration(this TimeSpans spans) => spans switch
    {
        TimeSpans.ThirtyMinutes => TimeSpan.FromMinutes(30),
        TimeSpans.OneHour => TimeSpan.FromHours(1),
        TimeSpans.ThreeHours => TimeSpan.FromHours(3),
        TimeSpans.SixHours => TimeSpan.FromHours(6),
        TimeSpans.TwelveHours => TimeSpan.FromHours(12),
        TimeSpans.OneDay => TimeSpan.FromDays(1),
        _ => null,
    };

    /// <summary>The locale key the UI label comes from.</summary>
    public static string LocaleKey(this TimeSpans spans) => spans switch
    {
        TimeSpans.ThirtyMinutes => "TaskGroup.TimeSpan.30Minutes",
        TimeSpans.OneHour => "TaskGroup.TimeSpan.1Hour",
        TimeSpans.ThreeHours => "TaskGroup.TimeSpan.3Hour",
        TimeSpans.SixHours => "TaskGroup.TimeSpan.6Hour",
        TimeSpans.TwelveHours => "TaskGroup.TimeSpan.12Hour",
        TimeSpans.OneDay => "TaskGroup.TimeSpan.1Day",
        _ => "TaskGroup.TimeSpan.Manual",
    };
}
