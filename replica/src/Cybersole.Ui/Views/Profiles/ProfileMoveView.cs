using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Profiles;

/// <summary>
/// Picks the group a profile should move to. <c>Profiles.Context.MoveTo</c>.
///
/// <para>
/// R64: the third of the MoveTo trio (proxies in R61, accounts in R62). Profiles are the same
/// shape as accounts — a <c>GroupId</c> on the item and a list on the group — so both sides have
/// to be updated, and moving is not clone-plus-delete because the profile keeps its Id.
/// </para>
///
/// <para>
/// <b>Which group type.</b> There are two identical classes in the model:
/// <c>Cybersole.Core.Models.ProfileGroup</c> and <c>BillingGroup</c>. They have the same four
/// members (Id, Name, Order, Profiles). Only <c>BillingGroup</c> is ever constructed — the
/// configuration stores <c>List&lt;BillingGroup&gt; BillingGroups</c> — so
/// <c>ProfileGroup</c> is a duplicate that nothing instantiates. This view uses the one that is
/// actually wired; see <c>ProfileGroupIsNotUsed</c> in the tests.
/// </para>
/// </summary>
public sealed class ProfileMoveView : UserControl
{
    private readonly ComboBox _groups;

    public ProfileMoveView(IReadOnlyList<BillingGroup> groups, BillingGroup? current)
    {
        var names = groups.Select(g => g.Name).ToList();
        var index = current is null
            ? 0
            : Math.Max(0, groups.ToList().FindIndex(g => g.Id == current.Id));

        _groups = new ComboBox
        {
            ItemsSource = names,
            SelectedIndex = names.Count > 0 ? index : -1,
            PlaceholderText = "Select group",
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch,
        };

        Content = UiKit.Scroll(UiKit.Form(
            UiKit.Row("Move to", _groups),
            UiKit.Caption(// R66: <= 1, not == 0 — with one group the Move button was a no-op.
                groups.Count <= 1
                ? "There is no other group to move to — create one first."
                : "The profile keeps its card and address; only its group changes.")));
    }

    /// <summary>The chosen group, or null when nothing was selected.</summary>
    public BillingGroup? Chosen(IReadOnlyList<BillingGroup> groups) =>
        _groups.SelectedIndex < 0 || _groups.SelectedIndex >= groups.Count
            ? null
            : groups[_groups.SelectedIndex];

    /// <summary>
    /// Moves the profile into the chosen group. Returns false when there was no window to host it.
    /// </summary>
    public static bool Show(Control owner, Profile profile, IReadOnlyList<BillingGroup> groups,
        BillingGroup? current, Action onMoved)
    {
        var view = new ProfileMoveView(groups, current);

        var move = UiKit.Button("Move", () =>
        {
            var target = view.Chosen(groups);
            if (target is null) return;

            foreach (var group in groups) group.Profiles.Remove(profile);
            target.Profiles.Add(profile);
            profile.GroupId = target.Id;
            onMoved();

            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        });

        return ViewHostModal.Show(owner, "Move profile", view, 480, 260, move);
    }
}
