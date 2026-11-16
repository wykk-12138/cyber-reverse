using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The relative-time formatter behind the "last seen" column: a duration becomes one of seven locale strings.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_1410E2B60</c> in 5.18.32, decompiled via IDA. Its structure is a chain of divisions and comparisons:
///
/// <code>
/// v4 = (now - a1)                          // TimeSpan ticks
/// v5 = v4 / 864000000000                   // whole days
/// if (v5 &gt; 1)        DaysAgoFormat(v5)
/// else if (v5 == 1)  OneDayAgo
/// else if (hours(v4) &gt; 1)  HoursAgoFormat(hours)
/// else if (hours(v4) == 1)   OneHourAgo
/// else if (minutes(v4) &gt; 1) MinutesAgoFormat(minutes)
/// else if (minutes(v4) == 1) OneMinuteAgo
/// else                       JustNow
/// </code>
///
/// The six literal offsets it loads — <c>off_146EF0410</c>, <c>_0518</c>, <c>_0450</c>, <c>_0550</c>, <c>_04D0</c>,
/// <c>_0590</c>, <c>_0498</c> — and the seven <c>TimeAgo.*</c> keys in the shipped catalogue agree one for one, which is
/// what identifies this function rather than the decompilation alone (R729; the key names are what the candidate scan
/// grouped it by).
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the day step is <c>ticks / 864000000000</c> — whole days, truncated.
///   Inference (high confidence): <c>sub_141D2FEB0</c> and <c>sub_141D2FFD0</c> are whole hours and whole minutes.
///     They are reached with the same <c>v4</c> and follow the identical <c>&gt;1</c> / <c>==1</c> pattern, and a
///     "3 days ago" value would be nonsense if the hour step read the 0-23 component instead.
///   Alternative not excluded: they could be <c>TimeSpan.Hours</c> / <c>TimeSpan.Minutes</c>. That reading makes the
///     single-unit branches reachable only inside a day, which contradicts nothing in the code I read but produces
///     wrong output for anything over a day, where the day branch already fires.
/// </summary>
public static class RelativeTime
{
    /// <summary>Formats an elapsed duration using the seven <c>TimeAgo.*</c> keys.</summary>
    /// <param name="elapsed">How long ago the event happened. Negative values are treated as "just now".</param>
    /// <param name="copy">Resolves a locale key to its text; receives the key, returns the text.</param>
    public static string Describe(TimeSpan elapsed, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        long ticks = elapsed.Ticks;
        if (ticks < 0)
        {
            ticks = 0;
        }

        long days = ticks / TimeSpan.TicksPerDay;
        if (days > 1)
        {
            return Format(copy("TimeAgo.DaysAgoFormat"), days);
        }

        if (days == 1)
        {
            return copy("TimeAgo.OneDayAgo");
        }

        long hours = ticks / TimeSpan.TicksPerHour;
        if (hours > 1)
        {
            return Format(copy("TimeAgo.HoursAgoFormat"), hours);
        }

        if (hours == 1)
        {
            return copy("TimeAgo.OneHourAgo");
        }

        long minutes = ticks / TimeSpan.TicksPerMinute;
        if (minutes > 1)
        {
            return Format(copy("TimeAgo.MinutesAgoFormat"), minutes);
        }

        if (minutes == 1)
        {
            return copy("TimeAgo.OneMinuteAgo");
        }

        return copy("TimeAgo.JustNow");
    }

    /// <summary>
    /// The original calls a two-argument format helper with the count; a catalogue entry without a placeholder would
    /// throw under <see cref="string.Format(string, object)"/>, so a missing placeholder returns the text unchanged.
    /// </summary>
    private static string Format(string text, long count)
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, count) : text;
}
