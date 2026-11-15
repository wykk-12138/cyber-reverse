using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// Picks the group a proxy should move to. <c>Proxies.Context.MoveTo</c>.
///
/// <para>
/// R61: the locale has MoveTo for proxies, accounts and tasks. This is the proxies one — the
/// smallest of the three, because a proxy belongs to exactly one group and reparenting it is a
/// single assignment.
/// </para>
///
/// <para>
/// Move is not clone-plus-delete: the row keeps its Id, its Usage and its measured status, because
/// moving a proxy between groups does not make its history untrue. Only <c>GroupId</c> changes.
/// </para>
/// </summary>
public sealed class ProxyMoveView : UserControl
{
    private readonly ComboBox _groups;

    public ProxyMoveView(IReadOnlyList<ProxyGroup> groups, ProxyGroup? current)
    {
        var names = groups.Select(g => g.Name).ToList();
        var index = current is null ? 0 : Math.Max(0, groups.ToList().FindIndex(g => g.Id == current.Id));

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
                : "The proxy keeps its usage history; only its group changes.")));
    }

    /// <summary>The chosen group, or null when nothing was selected.</summary>
    public ProxyGroup? Chosen(IReadOnlyList<ProxyGroup> groups) =>
        _groups.SelectedIndex < 0 || _groups.SelectedIndex >= groups.Count
            ? null
            : groups[_groups.SelectedIndex];

    /// <summary>
    /// Opens the picker and applies the choice. Returns false when there was no window to host it.
    /// </summary>
    /// <remarks>
    /// The confirm button is built here rather than inside the view: the view is a control, and
    /// closing the modal is the modal's job.
    /// </remarks>
    public static bool Show(Control owner, Proxy proxy, IReadOnlyList<ProxyGroup> groups,
        ProxyGroup? current, Action onMoved)
    {
        var view = new ProxyMoveView(groups, current);

        var move = UiKit.Button("Move", () =>
        {
            var target = view.Chosen(groups);
            if (target is null) return;

            // Reparent by id only. The proxy object stays in whichever list the caller keeps;
            // GroupId is what routing reads.
            proxy.GroupId = target.Id;
            onMoved();
            CloseOwner(owner);
        });

        var opened = ViewHostModal.Show(owner, "Move proxy", view, 480, 260, move);
        return opened;
    }

    /// <summary>Closes the modal that owns <paramref name="owner"/> after a successful move.</summary>
    private static void CloseOwner(Control owner)
    {
        if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
    }
}
