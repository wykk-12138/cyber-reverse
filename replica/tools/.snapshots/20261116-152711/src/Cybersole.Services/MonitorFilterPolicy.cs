using Cybersole.Core.Models;

namespace Cybersole.Services;

/// <summary>
/// Maps a store module id onto the settings.monitorFilters switches.
/// The original disables monitoring per store family from the Settings page;
/// the task engine consults this policy before starting a worker.
/// </summary>
public static class MonitorFilterPolicy
{
    public static bool IsEnabled(MonitorFilters filters, string storeId) => storeId.ToLowerInvariant() switch
    {
        "shopify" or "kith" => filters.Shopify,
        "nike" or "yeezysupply" or "confirmed" => filters.Nike,
        "footsites" => filters.Footsites,
        "supreme" => filters.Supreme,
        "offspring" => filters.OffSpringOrOffice,
        "popmart" => filters.PopMart,
        _ => true, // custom stores and everything not listed are always allowed
    };

    /// <summary>Store ids currently switched off (used for UI badges / logs).</summary>
    public static IReadOnlyList<string> Disabled(MonitorFilters filters)
        => new[]
        {
            ("shopify", filters.Shopify),
            ("kith", filters.Shopify),
            ("nike", filters.Nike),
            ("yeezysupply", filters.Nike),
            ("footsites", filters.Footsites),
            ("supreme", filters.Supreme),
            ("offspring", filters.OffSpringOrOffice),
            ("popmart", filters.PopMart),
        }
        .Where(x => !x.Item2)
        .Select(x => x.Item1)
        .ToList();
}
