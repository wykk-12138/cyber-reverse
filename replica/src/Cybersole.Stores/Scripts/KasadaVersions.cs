namespace Cybersole.Stores.Scripts;

/// <summary>
/// WHY THIS EXISTS: the original keys the sensor build per store — the image carries seven
/// "&lt;Store&gt;-Kasada-Version" settings entries (addresses in docs/KASADA/11 5.75) because each site runs
/// its own deployment of the sensor. A single shared value would be wrong for whichever stores differ.
/// <para>
/// Only the values actually observed are pinned here; an unmeasured store answers null so the caller's
/// fallback chain keeps going. An invented build string is worse than none at all, because the gate
/// compares x-kpsdk-v against what the site's own script published: a wrong guess fails the same way a
/// missing one does, but looks deliberate. The authoritative source is still the header the sensor stamps on its own request; this
/// table exists for when that header cannot be observed (offline replay, cached script).
/// </para>
/// </summary>
public static class KasadaVersions
{
    /// <summary>
    /// The build the payload reports today. Measured against the live site on 2026-11-18: the sensor served
    /// from api.nike.com stamps <c>x-kpsdk-v: j-1.2.992</c> on its own /mfc request. The value recorded
    /// earlier from the binary's string pool was j-1.2.988, which is what the build in hand shipped — the
    /// live deployment has moved on, so the observed value wins.
    /// </summary>
    public const string Observed = "j-1.2.992";

    /// <summary>
    /// Store key → x-kpsdk-v. Keys are the store's short name, matched case-insensitively; the three
    /// Crocs entries stay distinct because the image keeps them distinct.
    /// </summary>
    private static readonly Dictionary<string, string> ByStore = new(StringComparer.OrdinalIgnoreCase)
    {
        ["converse"] = Observed,
        ["crocs"] = Observed,
        ["crocs-eu"] = Observed,
        ["crocs-jp"] = Observed,
        ["footsites"] = Observed,
        ["nike"] = Observed,
        ["scheels"] = Observed,
    };

    /// <summary>
    /// The version for a store, or null when nothing has been measured for it. Null rather than a default
    /// on purpose: this table is one link in a fallback chain, and claiming a build for a store we have not
    /// measured would stop the chain at a guess instead of letting it continue.
    /// </summary>
    public static string? For(string? store) =>
        !string.IsNullOrWhiteSpace(store) && ByStore.TryGetValue(store!.Trim(), out var v) ? v : null;

    /// <summary>
    /// The seven settings keys the image carries, verbatim. Store short names come from the same
    /// convention, which is what lets <see cref="For"/> answer for each of them.
    /// </summary>
    public static IReadOnlyList<string> SettingKeys { get; } = new[]
    {
        "Converse-Kasada-Version",
        "Crocs-EU-Kasada-Version",
        "Crocs-JP-Kasada-Version",
        "Crocs-Kasada-Version",
        "Footsites-Kasada-Version",
        "Nike-Kasada-Version",
        "Scheels-Kasada-Version",
    };

    /// <summary>Maps a settings key such as "Crocs-EU-Kasada-Version" onto its store short name.</summary>
    public static string? StoreOfSetting(string settingKey)
    {
        const string suffix = "-Kasada-Version";
        if (string.IsNullOrWhiteSpace(settingKey)) return null;
        var key = settingKey.Trim();
        return key.EndsWith(suffix, StringComparison.OrdinalIgnoreCase)
            ? key[..^suffix.Length].ToLowerInvariant()
            : null;
    }
}
