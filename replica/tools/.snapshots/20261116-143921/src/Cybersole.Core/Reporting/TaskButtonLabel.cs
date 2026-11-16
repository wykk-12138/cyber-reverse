using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The task creator's primary-button label: four texts chosen by whether the action saves and how many tasks are
/// selected.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_140594500</c> in 5.18.32, decompiled via IDA. The body reads two properties off the model — a byte flag
/// (property 0) and a count (property 1, <c>HIDWORD(v26)</c>) — and then:
///
/// <code>
/// if (flag)                          // save
/// {
///     if (count == 1) return &amp;off_146EB85E8;    // singular
///     // else falls through to the shared plural path
/// }
/// else if (count &gt;= 2)              // create
/// {
///     goto plural;
/// }
/// // neither: the create-mode remainder
/// return &amp;off_146EB8538;
///
/// plural:
///     slot = flag ? &amp;off_146EB8638 : &amp;off_146EB8588;
///     return string.Format(localise(slot), count);
/// </code>
///
/// The two comparisons are <b>not the same</b>, and that asymmetry is the interesting part: save tests
/// <c>count == 1</c>, so a count of zero takes the plural; create tests <c>count &gt;= 2</c>, so a count of zero takes
/// the singular. Writing <c>count &gt; 1</c> in both branches would be wrong for zero in save mode.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the branch order, both comparisons, and the four distinct slots.
///   Observation: the catalogue holds exactly four <c>TaskCreator.Button.*</c> keys whose English is
///     "Save Task", "Save {0} Tasks", "Create Task", "Create {0} Tasks".
///   Inference (high confidence): which slot is which key. Resolving the slots to string objects did not work -- all
///     four read back the same implausible length, so they are descriptors rather than string pointers (R731) -- and
///     the assignment rests on the branch shape plus the absence of any other consistent assignment.
///   Not established: the identity of either property. The flag is read as "save" because that is the only reading in
///     which the four texts form two pairs.
/// </summary>
public static class TaskButtonLabel
{
    /// <summary>
    /// Returns the label for the primary button.
    /// </summary>
    /// <param name="saving">The model's first property: true when the button will save rather than create.</param>
    /// <param name="count">The model's second property: how many tasks are selected.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static string Describe(bool saving, int count, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        if (saving)
        {
            // count == 1 exactly; zero falls through to the plural arm
            if (count == 1)
            {
                return copy("TaskCreator.Button.SaveTask");
            }

            return Format(copy("TaskCreator.Button.SaveTasksFormat"), count);
        }

        // count >= 2 takes the plural; zero and one take the singular
        if (count >= 2)
        {
            return Format(copy("TaskCreator.Button.CreateTasksFormat"), count);
        }

        return copy("TaskCreator.Button.CreateTask");
    }

    private static string Format(string text, int count)
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, count) : text;
}
