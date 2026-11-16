using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>
/// Billing-profile allocation rules:
/// <list type="bullet">
/// <item>profile.oneCheckout — a profile that already produced an order is retired</item>
/// <item>taskGroup.profileLimit — the group may only burn through N profiles</item>
/// </list>
/// Pure functions so the policy is testable without the engine.
/// </summary>
public static class ProfileAllocation
{
    /// <summary>Picks the first candidate that is still allowed to check out.</summary>
    public static Profile? Select(IEnumerable<Profile> candidates,
        IReadOnlyDictionary<string, int> usage, int profileLimit = 0)
    {
        var used = 0;
        foreach (var profile in candidates)
        {
            var count = usage.TryGetValue(profile.Id, out var c) ? c : 0;
            if (profile.OneCheckout && count > 0) continue;   // retired after one order
            if (profileLimit > 0 && used >= profileLimit) break;
            used++;
            return profile;
        }

        return null;
    }

    /// <summary>How many distinct profiles the group has already burned through.</summary>
    public static int DistinctUsed(IEnumerable<Profile> candidates, IReadOnlyDictionary<string, int> usage)
        => candidates.Count(p => usage.TryGetValue(p.Id, out var c) && c > 0);

    /// <summary>True when the group still has a usable profile.</summary>
    public static bool HasCapacity(IEnumerable<Profile> candidates,
        IReadOnlyDictionary<string, int> usage, int profileLimit = 0)
        => Select(candidates, usage, profileLimit) is not null;
}
