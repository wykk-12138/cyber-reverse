using System.Windows.Input;
using Avalonia.Controls;
using Cybersole.Core;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// Edits one proxy group.
///
/// <para>
/// R54: the original has <c>Cybersole.Ui.Views.Proxies.Modals.ProxyGroupView</c>, and its XAML
/// binds three properties on <c>Cybersole.Models.ProxyGroup</c>:
/// </para>
///
/// <code>
/// ProxyGroupView,Cybersole.TimeSpans!Property  → ProxyGroup,Core.UsageExpiry!Property
/// ProxyGroup.MaxUsage   "Max usage"
/// ProxyGroup.Behaviour  "Behaviour"
/// </code>
///
/// <para>
/// This replica had none of them on screen. <c>ProxyGroup</c> carried MaxUsage, Behaviour and
/// UsageExpiry from the start, and the proxies page rendered a text line per group — so the
/// fields existed, the type was there, and nothing could set them.
/// </para>
///
/// <para>
/// UsageExpiry was also the wrong type until R54 (a DateTime? beside a separate TimeSpan?
/// UsagePeriod); that is now a <see cref="TimeSpans"/>, matching TaskGroup.
/// </para>
/// </summary>
public sealed class ProxyGroupView : UserControl
{

    /// <summary>
    /// Deletes a proxy group from the configuration (bound as <c>Delete</c>). This view only edits ONE group — it has no
    /// list and no services handle — so the caller passes the list it came from; false when the group is not in it.
    /// </summary>
    public bool Delete(IList<ProxyGroup> from)
    {
        if (from is null || !from.Remove(_group)) return false;

        return true;
    }

    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool CloseCore()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

    private readonly ProxyGroup _group;

    /// <summary>The group being edited (bound as <c>Draft</c>).</summary>
    public ProxyGroup Draft => _group;

    /// <summary>Bound as <c>Close</c>; closes the hosting window (was a bool method).</summary>
    public ICommand Close { get; }

    public ProxyGroupView(ProxyGroup group)
    {
        Close = new RelayCommand(() => CloseCore());

        _group = group;
        Content = Build();
    }

    private Control Build()
    {
        var name = UiKit.Text(_group.Name, watermark: "Group 1");
        var maxUsage = UiKit.Number(_group.MaxUsage);
        var behaviourValues = Enum.GetValues<ProxyGroupBehaviour>();
        var behaviour = UiKit.Combo(
            behaviourValues.Select(b => b.ToString()).ToList(),
            Math.Max(0, Array.IndexOf(behaviourValues, _group.Behaviour)),
            i => _group.Behaviour = behaviourValues[Math.Clamp(i, 0, behaviourValues.Length - 1)]);

        var spanValues = Enum.GetValues<TimeSpans>();

        // R66: the list needs a "not set" entry. With only the seven enum values, a group whose
        // UsageExpiry is null fell back to index 0 and displayed "ThirtyMinutes" — while the
        // caption beside it correctly said "No reset window". Worse, picking anything or pressing
        // Save turned the placeholder into a real 30-minute window. A screenshot found it; the
        // unit tests only ever asked what NextReset returns, not what the box shows first.
        var spanLabels = new List<string> { "(none)" };
        spanLabels.AddRange(spanValues.Select(t => t.ToString()));

        var span = UiKit.Combo(
            spanLabels,
            _group.UsageExpiry is null ? 0 : Array.IndexOf(spanValues, _group.UsageExpiry.Value) + 1,
            i => _group.UsageExpiry = i <= 0
                ? null
                : spanValues[Math.Clamp(i - 1, 0, spanValues.Length - 1)]);

        name.TextChanged += (_, _) => _group.Name = name.Text ?? string.Empty;
        maxUsage.TextChanged += (_, _) =>
        {
            if (int.TryParse(maxUsage.Text, out var v)) _group.MaxUsage = v;
        };

        // The derived boundary is shown, not edited: NextReset has no setter in the original.
        var resetNotice = UiKit.Caption(_group.NextReset is null
            ? "No reset window — limits do not roll over."
            : $"Limits reset at {_group.NextReset:u}.");

        return UiKit.Scroll(UiKit.Form(
            UiKit.Row("Group Name", name),
            UiKit.Row("Max usage", maxUsage),
            UiKit.Row("Behaviour", behaviour),
            UiKit.Row("Reset limits after", span),
            resetNotice,
            UiKit.Caption("Behaviour decides how a proxy is picked from this group.")));
    }

    /// <summary>Opens the editor modally; returns false when there is no window to own it.</summary>
    public static bool Show(Control owner, ProxyGroup group) =>
        ViewHostModal.Show(owner, string.IsNullOrWhiteSpace(group.Name) ? "Group Settings" : group.Name,
            new ProxyGroupView(group), width: 560, height: 420);
}
