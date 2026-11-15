using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>
/// Per-task execution policy: whether a task is allowed to spend money, and which solver
/// a group-level Cloudflare setting should prefer.
/// </summary>
public static class TaskPolicy
{
    /// <summary>
    /// <c>botTask.monitorMode</c> — monitor-only tasks report availability but never check out.
    /// Useful to validate a URL/size run before letting it buy anything.
    /// </summary>
    public static bool ShouldCheckout(BotTask task)
        => !task.MonitorMode;

    /// <summary>Why a checkout was skipped (for the log line).</summary>
    public static string? SkipReason(BotTask task)
        => task.MonitorMode ? "monitor-only task (botTask.monitorMode)" : null;

    /// <summary>
    /// <c>taskGroup.cloudflareSolver</c> — a group may pin a specific solver; empty falls back
    /// to the globally configured one.
    /// </summary>
    public static string ResolveSolver(TaskGroup? group, string globalSolver)
        => string.IsNullOrWhiteSpace(group?.CloudflareSolver)
            ? globalSolver
            : group!.CloudflareSolver!.Trim();
}
