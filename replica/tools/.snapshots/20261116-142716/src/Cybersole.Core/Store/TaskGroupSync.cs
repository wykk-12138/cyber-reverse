using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>
/// settings.group.linkedDelays behaviour: when a group links its delays, editing one task's
/// monitor/retry values pushes them to every sibling. Pure function so the rule is testable.
/// </summary>
public static class TaskGroupSync
{
    /// <summary>
    /// Copies the edited task's delays onto its siblings. Returns how many tasks were touched.
    /// A group with <see cref="TaskGroup.LinkedDelays"/> off is a no-op.
    /// </summary>
    public static int ApplyLinkedDelays(TaskGroup group, BotTask edited)
    {
        if (!group.LinkedDelays) return 0;

        var touched = 0;
        foreach (var task in group.Tasks)
        {
            if (ReferenceEquals(task, edited)) continue;
            task.MonitorDelay = edited.MonitorDelay;
            task.RetryDelay = edited.RetryDelay;
            touched++;
        }

        return touched;
    }

    /// <summary>Group-wide checkout budget: how many more checkouts the group may attempt.</summary>
    public static int RemainingCheckouts(TaskGroup group, int alreadyCompleted)
        => (group.CheckoutLimit ?? 0) <= 0 ? int.MaxValue : Math.Max(0, (group.CheckoutLimit ?? 0) - alreadyCompleted);
}
