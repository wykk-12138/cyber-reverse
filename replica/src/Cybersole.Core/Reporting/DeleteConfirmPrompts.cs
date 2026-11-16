using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The family of delete confirmations: each screen names its own count in a title, a message and an action button,
/// and shows nothing when the count is zero.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// Four members of this family have been decompiled, and they are the same function with different strings:
///
///   <c>sub_140579E40</c>  store groups   R732   guard: <c>if (count)</c>                one or two placeholders
///   <c>sub_140641190</c>  size presets   R734   guard: <c>if (count != 0)</c>           two texts
///   <c>sub_1405AAA60</c>  tasks          R735   guard: a helper call                 three texts
///
/// For the tasks screen the body is:
/// <code>
/// if (predicate(...))                      // falsy -> the whole body is skipped
/// {
///     count = model[8][16];
///     title   = format(&amp;off_146EBA8A0, count);
///     message = format(&amp;off_146EBA848, count);
///     dialog(title, message, 1);
///     dialog[528] = format(&amp;off_146EBA7F0, count);   // the action button
/// }
/// </code>
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation (tasks): three slots, each formatted with the same count, and a guard that skips everything.
///   Inference (high confidence): the slot-to-key assignment, from the argument order the shared dialog builder
///     uses — title first, message second — established by R732 and consistent in all four bodies read so far.
///   Inference (medium): that the tasks guard is a zero test. R732 and R734 both test the count explicitly; here it
///     is a call into a helper whose semantics were not resolved. The zero rule is carried over from the siblings.
///   NOT established: whether the other five screens (accounts, proxies, profiles, account groups, and the second
///     accounts function) guard the same way. Their keys exist and their text shapes match, but their bodies have not
///     been read, so <see cref="TasksDeleteConfirm"/> is the only screen wired here.
/// </summary>
public static class DeleteConfirmPrompts
{
    /// <summary>The task grid's delete confirmation: three texts, all carrying the selection count.</summary>
    public static (string Title, string Message, string Action)? Tasks(int count, Func<string, string> copy)
        => Build("Tasks.DeleteConfirm", count, copy);

    /// <summary>
    /// Builds a screen's confirmation from its key prefix, or returns <c>null</c> for an empty selection.
    /// </summary>
    internal static (string Title, string Message, string Action)? Build(
        string prefix, int count, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        if (count == 0)
        {
            return null;
        }

        return (
            Format(copy(prefix + ".TitleFormat"), count),
            Format(copy(prefix + ".MessageFormat"), count),
            Format(copy(prefix + ".ActionFormat"), count));
    }

    private static string Format(string text, int count)
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, count) : text;
}
