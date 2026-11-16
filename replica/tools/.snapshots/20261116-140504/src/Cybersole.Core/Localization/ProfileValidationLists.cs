using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Cybersole.Core.Localization;

/// <summary>
/// Country and state lists used by the profile CSV row validator.
///
/// WHY THIS EXISTS (AGENTS.md §1.2 requires the reason be stated):
/// The binding/copy metrics can tell that the two locale keys `ProfileCsv.Error.UnknownCountry` and
/// `ProfileCsv.Error.UnknownState` exist, but not that anything emits them -- so they sat as copy gaps for
/// many rounds. R702 decompiled the guards that raise them and R703 verified both functions plus the
/// instruction bytes; R704 exported the English tables (244 countries, 50 states, 50 abbreviations, zero
/// alignment anomalies) with <c>analysis/export_profile_lists.py</c>. This class is the runtime half: the
/// replica's validator must check against the same lists the original does, otherwise implementing the
/// message would be a guess dressed as a feature.
///
/// Shape mirrors the original (Observation, from the decompiled guards):
///   * the country list is per-locale -- one copy per language, as the fake-data tables are;
///   * a state list belongs to a country row, and most countries have none;
///   * comparison is trim-then-ordinal-ignore-case; there is no lowercasing and no abbreviation matching;
///   * a country with no state list is silently accepted rather than rejected.
/// </summary>
public static class ProfileValidationLists
{
    private const string ResourceName = "Cybersole.ProfileValidation.en.json";

    private static readonly Lazy<Payload?> Data = new(Load, isThreadSafe: true);

    /// <summary>Every country the original knows, in its own order.</summary>
    public static IReadOnlyList<string> Countries => Data.Value?.Country ?? Array.Empty<string>();

    /// <summary>
    /// The states for one country, or empty when that country carries no state list.
    /// An empty result means "no constraint" -- the guard returns before comparing.
    /// </summary>
    public static IReadOnlyList<string> StatesFor(string? country)
    {
        var payload = Data.Value;
        if (payload is null || string.IsNullOrWhiteSpace(country))
        {
            return Array.Empty<string>();
        }

        // Only countries whose rows carry a state list appear here. In the English tables that is the
        // United States; the German/Austrian/Arabic lists belong to their own locale copies.
        var key = Normalise(country);
        if (payload.StateOwners is null)
        {
            return Array.Empty<string>();
        }

        foreach (var pair in payload.StateOwners)
        {
            if (Normalise(pair.Key).Equals(key, StringComparison.OrdinalIgnoreCase))
            {
                return pair.Value ?? Array.Empty<string>();
            }
        }

        return Array.Empty<string>();
    }

    /// <summary>Trim then ordinal-ignore-case containment, matching the decoded comparison chain.</summary>
    public static bool ContainsCountry(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return true;   // blank passes: the guard returns before looking anything up
        }

        var needle = Normalise(value);
        foreach (var country in Countries)
        {
            if (Normalise(country).Equals(needle, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// True when the state is acceptable for the country. A country with no state list accepts anything,
    /// which is what the original does rather than raising an error.
    /// </summary>
    public static bool ContainsState(string? country, string? state)
    {
        var states = StatesFor(country);
        if (states.Count == 0)
        {
            return true;
        }

        if (string.IsNullOrWhiteSpace(state))
        {
            return true;
        }

        var needle = Normalise(state);
        foreach (var candidate in states)
        {
            if (Normalise(candidate).Equals(needle, StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }
        }

        return false;
    }

    private static string Normalise(string value) => value.Trim();

    /// <summary>
    /// The list's own spelling for a country the caller matched, so the state message can name it the way the
    /// original does (the guard reads the country row's name field, not the value the user typed).
    /// Returns the trimmed input when nothing matched, which only happens on a path that already failed.
    /// </summary>
    public static string CanonicalCountryName(string? country)
    {
        if (string.IsNullOrWhiteSpace(country))
        {
            return string.Empty;
        }

        var needle = Normalise(country);
        foreach (var candidate in Countries)
        {
            if (Normalise(candidate).Equals(needle, StringComparison.OrdinalIgnoreCase))
            {
                return candidate;
            }
        }

        return needle;
    }

    private static Payload? Load()
    {
        try
        {
            var assembly = typeof(ProfileValidationLists).Assembly;
            using var stream = assembly.GetManifestResourceStream(ResourceName);
            if (stream is null)
            {
                return null;
            }

            using var reader = new StreamReader(stream);
            var json = reader.ReadToEnd();
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var countries = root.TryGetProperty("country", out var c)
                ? c.EnumerateArray().Select(e => e.GetString() ?? string.Empty).Where(s => s.Length > 0).ToArray()
                : Array.Empty<string>();

            // The exported file carries one flat state list plus the country it belongs to. Record the owner
            // explicitly instead of guessing it, so adding another locale's list later cannot silently
            // re-point every country at one country's states.
            var owner = root.TryGetProperty("state_owner", out var o) ? o.GetString() : null;
            string[] states = root.TryGetProperty("state", out var s)
                ? s.EnumerateArray().Select(e => e.GetString() ?? string.Empty).Where(x => x.Length > 0).ToArray()
                : Array.Empty<string>();

            var owners = new Dictionary<string, string[]>();
            if (!string.IsNullOrWhiteSpace(owner) && states.Length > 0)
            {
                owners[owner!] = states;
            }

            return new Payload(countries, owners);
        }
        catch (Exception)
        {
            // A validation table that cannot be read must not make the editor unusable; the guards then
            // behave as "no country list known", which accepts everything.
            return null;
        }
    }

    private sealed class Payload
    {
        public Payload(string[] country, Dictionary<string, string[]> stateOwners)
        {
            Country = country;
            StateOwners = stateOwners;
        }

        public string[] Country { get; }

        public Dictionary<string, string[]> StateOwners { get; }
    }
}
