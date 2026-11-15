using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>
/// Task-group presentation order (settings.pinGroups behaviour): pinned groups float to the top,
/// otherwise the user's own ordering is preserved. Pure function so the rule is testable.
/// </summary>
public static class TaskGroupOrdering
{
    /// <summary>Pinned groups first, then the rest — relative order kept inside each bucket.</summary>
    public static IReadOnlyList<TaskGroup> Sort(IEnumerable<TaskGroup> groups)
    {
        var all = groups.ToList();
        return all.Where(g => g.Pinned)
            .Concat(all.Where(g => !g.Pinned))
            .ToList();
    }

    /// <summary>Number of tasks that will be visible at the top of the page.</summary>
    public static int PinnedTaskCount(IEnumerable<TaskGroup> groups)
        => groups.Where(g => g.Pinned).Sum(g => g.Tasks.Count);
}
