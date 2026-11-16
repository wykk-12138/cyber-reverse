using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Accounts;

/// <summary>
/// Picks the group an account should move to. <c>Accounts.Context.MoveTo</c>.
///
/// <para>
/// R62: same shape as <see cref="Cybersole.Ui.Views.Proxies.ProxyMoveView"/>, different type. An
/// account belongs to exactly one group, so reparenting is a single assignment — the difference
/// from the proxy case is that <c>Account</c> stores the group as a plain
/// <c>GroupId</c> string and the group stores a list, so both sides have to agree.
/// </para>
///
/// <para>
/// Move is not clone-plus-delete: the account keeps its Id, its password and its creation date.
/// </para>
/// </summary>
public sealed class AccountMoveView : UserControl
{
    private readonly ComboBox _groups;

    public AccountMoveView(IReadOnlyList<AccountGroup> groups, AccountGroup? current)
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
                : "The account keeps its credentials; only its group changes.")));
    }

    /// <summary>The chosen group, or null when nothing was selected.</summary>
    public AccountGroup? Chosen(IReadOnlyList<AccountGroup> groups) =>
        _groups.SelectedIndex < 0 || _groups.SelectedIndex >= groups.Count
            ? null
            : groups[_groups.SelectedIndex];

    /// <summary>
    /// Opens the picker and moves the account. Returns false when there was no window to host it.
    /// </summary>
    /// <remarks>
    /// Both sides are updated: the destination group gets the account, and the account's
    /// <c>GroupId</c> is repointed. Updating only one would leave the tree and the reference
    /// disagreeing about where the account lives.
    /// </remarks>
    public static bool Show(Control owner, Account account, IReadOnlyList<AccountGroup> groups,
        AccountGroup? current, Action onMoved)
    {
        var view = new AccountMoveView(groups, current);

        var move = UiKit.Button("Move", () =>
        {
            var target = view.Chosen(groups);
            if (target is null) return;

            // Remove from whichever group currently holds it, then add to the target.
            foreach (var group in groups)
                group.Accounts.Remove(account);

            target.Accounts.Add(account);
            account.GroupId = target.Id;
            onMoved();

            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        });

        return ViewHostModal.Show(owner, "Move account", view, 480, 260, move);
    }
}
