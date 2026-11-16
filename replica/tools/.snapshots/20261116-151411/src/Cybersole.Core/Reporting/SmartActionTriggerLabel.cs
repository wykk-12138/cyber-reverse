using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The smart-action creator's trigger label, and the reason this family does not share one shape.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_1405FFFA0</c> in 5.18.32, all seventeen lines:
///
/// <code>
/// if (a2) {
///     box = *(QWORD*)(a2 + 24);              // a NAME, not a count
///     return format(&amp;off_146E912C8, box);   // "{0} Trigger"
/// } else
///     return localise(&amp;off_146E910C8);       // "No Trigger"
/// </code>
///
/// TWO sentences, not the three that <see cref="SmartActionSavedCounts"/> needs. That difference is not an accident of
/// these two functions: R751 read three members of this cluster and found the split follows the argument's kind.
///
/// <list type="bullet">
/// <item>Where the argument is a <b>count</b>, the family uses 0 / 1 / n, because a single item gets its own sentence
/// with the digit written out (<c>No Filters</c>, <c>1 Filter Saved</c>, <c>{0} Filters Saved</c>).</item>
/// <item>Where the argument is a <b>name</b>, there are two sentences and no middle case (this function).</item>
/// <item>Where the branch tests a <b>comparison</b> rather than a count, there are also two — <c>sub_1405FFD50</c>
/// returns <c>&amp;off_146E90B10</c> ("{0} if") in one arm and <c>&amp;off_146E90C18</c> in the other.</item>
/// </list>
///
/// So "the cluster is 0/1/n" would be a wrong generalisation, and the discriminator is the argument's type rather than
/// the screen. This matters for measuring coverage: only count-shaped labels have a placeholder-free sibling that a
/// placeholder-based ranking cannot see.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: all seventeen lines above, and the catalogue's "No Trigger" and "{0} Trigger".
///   Inference (high confidence): that "No Trigger" is the else-slot's text, from the two catalogue keys under
///     <c>SmartActionsCreator</c> that fit the two branches.
///   Unknown: the text behind <c>off_146E90C18</c> in <c>sub_1405FFD50</c>. <c>SmartActionsCreator.AlwaysRun</c>
///     ("This smart action will always run when triggered") reads like a plausible counterpart to "{0} if", but the slot
///     was not resolved, so that stays a guess rather than a mapping.
/// </summary>
public static class SmartActionTriggerLabel
{
    /// <summary>
    /// The trigger's label: the name it carries, or the "no trigger" sentence when there is none.
    /// </summary>
    /// <param name="trigger">The trigger's name, read from the record; null when no trigger is set.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static string Describe(string? trigger, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        if (trigger is null)
        {
            return copy("SmartActionsCreator.NoTrigger");
        }

        string text = copy("SmartActionsCreator.TriggerFormat");
        return text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, trigger) : text;
    }
}
