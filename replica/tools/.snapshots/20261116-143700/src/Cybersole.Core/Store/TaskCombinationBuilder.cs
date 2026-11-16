using Cybersole.Core.Expressions;
using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>Inputs for one bulk task creation (Cybersole.Ui.Views.Tasks.TaskCreatorView).</summary>
public sealed class TaskCombinationRequest
{
    public required string Store { get; init; }
    public string? Url { get; init; }

    /// <summary>Name template; supports <c>{store}</c> <c>{size}</c> <c>{profile}</c> <c>{index}</c>.</summary>
    public string? NameTemplate { get; init; }

    /// <summary>Sizes to multiply over. Empty means a single "default" task.</summary>
    public List<string> Sizes { get; init; } = new();

    /// <summary>Profile ids to multiply over. Empty means "let the engine allocate".</summary>
    public List<string> Profiles { get; init; } = new();

    public List<string> ProxyGroupIds { get; init; } = new();

    /// <summary>TaskCreator.QuantityPerProfile — how many tasks per (size, profile) pair.</summary>
    public int QuantityPerProfile { get; init; } = 1;

    /// <summary>TaskCreator.MultiCart — allow several carts from the same profile.</summary>
    public bool MultiCart { get; init; }

    public bool AutoQuantity { get; init; }
    public DateTime? StartTime { get; init; }
    public int? MonitorDelay { get; init; }
    public int? RetryDelay { get; init; }
    public int? Timeout { get; init; }
    public bool MonitorMode { get; init; }
    public bool PriceCheck { get; init; }
    public int CheckoutDelay { get; init; }
}

/// <summary>
/// Expands a <see cref="TaskCombinationRequest"/> into concrete tasks.
///
/// The original's creator multiplies the selected sizes by the selected profiles (and by
/// quantity-per-profile when multi-cart is on); this does the same, then names each task
/// through the expression engine so a bulk run is identifiable in the grid.
/// </summary>
public static class TaskCombinationBuilder
{
    /// <summary>Hard ceiling so a mis-typed quantity cannot create 100k tasks.</summary>
    public const int MaxTasks = 5000;

    public static IReadOnlyList<BotTask> Build(TaskCombinationRequest request)
    {
        var sizes = request.Sizes.Count > 0 ? request.Sizes : new List<string> { string.Empty };
        var profiles = request.Profiles.Count > 0 ? request.Profiles : new List<string> { string.Empty };
        var perPair = Math.Clamp(request.QuantityPerProfile, 1, 1000);

        // Multi-cart is what makes quantity-per-profile meaningful; without it one task per pair.
        var repeats = request.MultiCart ? perPair : 1;

        var taskName = string.IsNullOrWhiteSpace(request.NameTemplate)
            ? "{store} {size} {profile} {index}"
            : request.NameTemplate!;

        var tasks = new List<BotTask>();
        var index = 0;

        foreach (var size in sizes)
        {
            foreach (var profile in profiles)
            {
                for (var r = 0; r < repeats; r++)
                {
                    if (tasks.Count >= MaxTasks) break;

                    index++;
                    var vars = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
                    {
                        ["store"] = request.Store,
                        ["size"] = size,
                        ["profile"] = ShortId(profile),
                        ["index"] = index.ToString(),
                    };

                    var name = ExpressionEngine.Evaluate(taskName, vars).Trim();
                    if (name.Length == 0) name = $"{request.Store} task {index}";

                    tasks.Add(new BotTask
                    {
                        Name = name,
                        Store = request.Store,
                        Product = new Product
                        {
                            Url = request.Url,
                            Sizes = string.IsNullOrEmpty(size)
                                ? new List<string>()
                                : new List<string> { size },
                            PriceCheck = request.PriceCheck,
                        },
                        ProfileId = string.IsNullOrEmpty(profile) ? null : profile,
                        ProxyGroupId = PickProxyGroup(request.ProxyGroupIds, index),
                        StartTime = request.StartTime,
                        MonitorDelay = request.MonitorDelay,
                        RetryDelay = request.RetryDelay,
                        Timeout = request.Timeout,
                        MonitorMode = request.MonitorMode,
                        CheckoutDelay = request.CheckoutDelay,
                        Enabled = true,
                    });
                }
            }
        }

        return tasks;
    }

    /// <summary>Round-robin proxy-group assignment so no single group is over-used.</summary>
    private static string? PickProxyGroup(IReadOnlyList<string> groups, int index) =>
        groups.Count == 0 ? null : groups[(index - 1) % groups.Count];

    private static string ShortId(string value) =>
        value.Length <= 8 ? value : value[..8];

    /// <summary>How many tasks this request would create (used to warn before building).</summary>
    public static int Count(TaskCombinationRequest request)
    {
        var sizes = Math.Max(1, request.Sizes.Count);
        var profiles = Math.Max(1, request.Profiles.Count);
        var perPair = Math.Clamp(request.QuantityPerProfile, 1, 1000);
        var repeats = request.MultiCart ? perPair : 1;
        return Math.Min(MaxTasks, sizes * profiles * repeats);
    }
}
