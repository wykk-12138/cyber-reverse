using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The smart-action creator's two counters, each of which has three separate sentences: nothing saved, one saved, and
/// a formatted count.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_140600020</c> in 5.18.32, decompiled via IDA in full (31 lines):
///
/// <code>
/// v4 = a2;                                  // the count
/// if ((_DWORD)a2) {
///     if ((_DWORD)a2 == 1)
///         return localise(&amp;off_146E90CC8);        // "1 Filter Saved"
///     else {
///         box = v4;
///         return format(&amp;off_146E90D18, box);    // "{0} Filters Saved"
///     }
/// } else
///     return localise(&amp;off_146E91018);            // "No Filters"
/// </code>
///
/// So the split is <b>0 / 1 / n</b>, not 0 / n. The one case has its own sentence with the digit baked in, which is why
/// "{0} Filters Saved" is never the text for a count of one.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the three branches above and all three locale slots, for the filters counter.
///   Observation: the catalogue's three keys per counter — NoFilters/FilterOne/FiltersFormat, and the matching
///     NoActions/ActionOne/ActionsFormat — each with the text quoted here.
///   Inference (high confidence): <c>sub_1406000E0</c> is the same function for actions. It is the same 31-line body
///     with different slots, and its tail was read; its branches were not read line for line.
///   Inference (high confidence): the slot-to-key assignment, from the texts matching the branches' shapes.
/// </summary>
public static class SmartActionSavedCounts
{
    /// <summary>How many filters the smart action has, in the creator's wording.</summary>
    public static string Filters(int count, Func<string, string> copy)
        => Describe(count, "SmartActionsCreator.NoFilters",
            "SmartActionsCreator.FilterOne", "SmartActionsCreator.FiltersFormat", copy);

    /// <summary>How many actions the smart action has, in the creator's wording.</summary>
    public static string Actions(int count, Func<string, string> copy)
        => Describe(count, "SmartActionsCreator.NoActions",
            "SmartActionsCreator.ActionOne", "SmartActionsCreator.ActionsFormat", copy);

    /// <summary>
    /// The 0 / 1 / n split. The one case is a separate sentence, so a count of one never reaches the format.
    /// </summary>
    internal static string Describe(
        int count, string noneKey, string oneKey, string formatKey, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        if (count == 0)
        {
            return copy(noneKey);
        }

        if (count == 1)
        {
            return copy(oneKey);
        }

        string text = copy(formatKey);
        return text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, count) : text;
    }
}
