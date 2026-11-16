using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The smart-action "last run" label: which action fired and how many times.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_14061E0E0</c> in 5.18.32, decompiled via IDA:
///
/// <code>
/// v4 = property(0);
/// if (!v4) return 0;
/// if (*(void**)v4 != &amp;unk_144DB80B0) return 0;      // must be a string
/// v5 = *(QWORD*)(v4 + 8);
/// v6 = property(1);
/// if (!v6 || *(void**)v6 != &amp;unk_144C87DE0) return 0;   // must be an int32
/// v7 = *(DWORD*)(v6 + 8);
/// text = localise(&amp;off_146E90808);                    // "Triggered {0} ({1})"
/// </code>
///
/// The notable part is the two guards. Every type mismatch returns zero, so a malformed record produces no label
/// at all rather than a label with a blank or a zero in it. That is expressible in C# as "null in, null out".
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: both type guards, both early returns, the string and int32 reads, and the one locale slot.
///   Observation: <c>SmartActions.LastRun.Format</c> is the only catalogue sentence shaped "Triggered {0} ({1})".
///   Inference (high confidence): the string fills {0} and the int fills {1}, from the sentence reading
///     "Triggered &lt;action&gt; (&lt;count&gt;)". The format call itself is beyond the region examined.
///   NOT REPRESENTABLE: the type-tag comparisons. Here they can only fail if the record is malformed, which in the
///     replica's typed model cannot happen; the null cases are the part that can be mirrored, and they are.
/// </summary>
public static class SmartActionLastRun
{
    /// <summary>
    /// The label for an action's most recent run, or <c>null</c> when either field is missing — which is what the
    /// original does for a record whose property is absent or of the wrong type.
    /// </summary>
    /// <param name="action">The action's name; the original reads it as a string.</param>
    /// <param name="count">How many times it fired; the original reads it as an int32.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static string? Format(string? action, int? count, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        if (action is null || count is null)
        {
            return null;
        }

        string text = copy("SmartActions.LastRun.Format");
        return text.Contains("{0}", StringComparison.Ordinal)
            ? string.Format(text, action, count.Value)
            : text;
    }
}
