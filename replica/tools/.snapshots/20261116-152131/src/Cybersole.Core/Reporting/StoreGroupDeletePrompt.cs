using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The store-group delete confirmation: a title naming the group, and a message that gains a second clause when the
/// group is in use.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_140579E40</c> in 5.18.32, decompiled via IDA. It reads the group's name and a usage count, then:
///
/// <code>
/// v6 = usageCount(name)                       // how many smart action filters reference the group
/// if (v6)                                     // NOTE: truthiness, not &gt; 0
/// {
///     args = new object[2] { name, box(v6) };
///     message = localise(&amp;off_146F19900, args);   // two placeholders
/// }
/// else
/// {
///     args = new object[1] { name };
///     message = localise(&amp;off_146F19828, args);   // one placeholder
/// }
/// title = localise(&amp;off_146F19898, name);       // "Delete {0}?"
/// buttons: &amp;off_146B99640 (Delete), &amp;off_146B99578 (Cancel)
/// </code>
///
/// **The interesting part is the condition**: <c>if (v6)</c> tests truthiness, so a negative count takes the
/// two-argument branch. Writing <c>if (v6 &gt; 0)</c> is the natural thing to do and would differ for a count that
/// cannot legitimately be negative — recorded because it is what the binary does, not because a negative usage count
/// is meaningful.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the branch condition, the two argument counts, the four catalogue keys it loads, and the two button
///     keys.
///   Inference (high confidence): slot 0x146F19900 is <c>UsedMessageFormat</c> and 0x146F19828 is
///     <c>MessageFormat</c>. The branch that passes two arguments must take the text with two placeholders, and only
///     one of the two candidates has a <c>{1}</c>.
///   Out of scope here: the dialog itself. The decompiled tail boxes a confirmation model and calls the show helper
///     with a slot index; the replica's dialog plumbing is its own by design, and asserting "a dialog appeared" is a
///     window-level test rather than a behaviour probe.
/// </summary>
public static class StoreGroupDeletePrompt
{
    /// <summary>Builds the confirmation text for deleting a store group.</summary>
    /// <param name="name">The group's name, as shown in the grid.</param>
    /// <param name="usedBy">How many smart action filters reference it.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static (string Title, string Message) For(string name, int usedBy, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        string title = Format(copy("Utilities.StoreGroups.Delete.TitleFormat"), name);

        // truthiness, not a positivity test — a negative count takes the in-use text
        string message = usedBy != 0
            ? Format(copy("Utilities.StoreGroups.Delete.UsedMessageFormat"), name, usedBy)
            : Format(copy("Utilities.StoreGroups.Delete.MessageFormat"), name);

        return (title, message);
    }

    private static string Format(string text, params object[] args)
        // Only format when the template actually carries a placeholder; a translation slip should not throw here.
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, args) : text;
}
