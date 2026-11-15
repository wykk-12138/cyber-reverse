using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Common;

namespace Cybersole.Ui.Views.Tasks;

/// <summary>
/// Picks the group a task should move to. <c>Tasks.Context.MoveTo</c>.
///
/// <para>
/// R65: the last of the four MoveTo actions in the locale (proxies R61, accounts R62, profiles
/// R64). Same shape: the destination owns a list, the item carries a <c>GroupId</c>, and both have
/// to change or the tree and the reference disagree.
/// </para>
///
/// <para>
/// Move is not clone-plus-delete. The task keeps its Id and its product binding; a moved task is
/// the same task in a different group, which is why the engine's per-task state is untouched.
/// </para>
/// </summary>
public sealed class TaskMoveView : UserControl
{
    private readonly ComboBox _groups;

    public TaskMoveView(IReadOnlyList<TaskGroup> groups, TaskGroup? current)
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
            // R66: `<= 1`, not `== 0`. With a single group the dialog opened, listed that group,
            // and pressing Move did nothing — because the handler refuses a no-op move. The
            // caption said "only its group changes" and never mentioned there was nowhere to go.
            UiKit.Caption(groups.Count <= 1
                ? "There is no other group to move to — create one first."
                : "The task keeps its product and settings; only its group changes.")));
    }

    /// <summary>The chosen group, or null when nothing was selected.</summary>
    public TaskGroup? Chosen(IReadOnlyList<TaskGroup> groups) =>
        _groups.SelectedIndex < 0 || _groups.SelectedIndex >= groups.Count
            ? null
            : groups[_groups.SelectedIndex];

    /// <summary>
    /// Moves the task into the chosen group. Returns false when there was no window to host it.
    /// </summary>
    public static bool Show(Control owner, BotTask task, IReadOnlyList<TaskGroup> groups,
        TaskGroup? current, Action onMoved)
    {
        var view = new TaskMoveView(groups, current);

        var move = UiKit.Button("Move", () =>
        {
            var target = view.Chosen(groups);
            if (target is null) return;
            if (current is not null && target.Id == current.Id) return;   // no-op

            foreach (var group in groups) group.Tasks.Remove(task);
            target.Tasks.Add(task);
            task.GroupId = target.Id;
            onMoved();

            if (TopLevel.GetTopLevel(owner) is Window window) window.Close();
        });

        return ViewHostModal.Show(owner, "Move task", view, 480, 260, move);
    }
}
