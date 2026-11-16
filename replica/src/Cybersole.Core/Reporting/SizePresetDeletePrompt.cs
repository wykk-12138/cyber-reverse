using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The confirmation shown before deleting the selected size presets — and the fact that an empty selection shows
/// nothing at all.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_140641190</c> in 5.18.32, decompiled via IDA:
///
/// <code>
/// if (*(DWORD*)(*(a1 + 528)[8] + 16))          // selection count
/// {
///     count   = the same count
///     title   = format(&amp;off_146E891F8, count);
///     message = format(&amp;off_146E89188, count);
///     dialog(title, message, ...); show();
///     return;
/// }
/// return;                                       // count == 0: no dialog
/// </code>
///
/// **The guard is the behaviour worth pinning**: the whole function is skipped when the count is zero. A replica that
/// builds the dialog unconditionally would show "Are you sure you want to delete 0 sizes?" on an empty selection,
/// which the original never does.
///
/// A QUIRK IN THE SHIPPED TEXT, preserved rather than tidied: the title says "presets" and the message says "sizes".
/// That is what the catalogue contains -- <c>Settings.Sizes.DeleteConfirm.TitleFormat</c> is
/// "Delete {0} presets?" and <c>Settings.Sizes.DeleteConfirm.MessageFormat</c> is
/// "Are you sure you want to delete {0} sizes?\nYou cannot undo this action." -- so the replica keeps both spellings.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the zero guard, that one count feeds both texts, and the two slots.
///   Inference (high confidence): <c>off_146E891F8</c> is the title and <c>off_146E89188</c> the message, from the
///     argument order of the shared dialog builder, which the store-group case in R732 established.
///   Not established: whether the same function runs for the "presets" grid and the "sizes" grid, or whether two
///     grids share it. The strings disagree, so one of them is stale in the source.
/// </summary>
public static class SizePresetDeletePrompt
{
    /// <summary>
    /// Builds the confirmation, or returns <c>null</c> when nothing is selected — matching the original, which
    /// returns before building anything.
    /// </summary>
    /// <param name="count">How many presets are selected.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static (string Title, string Message)? For(int count, Func<string, string> copy)
        => ForPrefix("Settings.Sizes.DeleteConfirm", count, copy);

    /// <summary>
    /// The stores grid's confirmation. <c>sub_1406458F0</c> has the identical shape to the size presets one — a zero
    /// guard, an int32 boxed into two texts — so it shares the builder. Its catalogue copy, however, is a shipped bug
    /// worth keeping: this is the <b>stores</b> screen and both of its texts say "presets".
    /// </summary>
    public static (string Title, string Message)? Stores(int count, Func<string, string> copy)
        => ForPrefix("Settings.Stores.DeleteConfirm", count, copy);

    private static (string Title, string Message)? ForPrefix(string prefix, int count, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        // the decompiled guard is a zero test on the count, not a positivity test
        if (count == 0)
        {
            return null;
        }

        string title = Format(copy(prefix + ".TitleFormat"), count);
        string message = Format(copy(prefix + ".MessageFormat"), count);
        return (title, message);
    }

    private static string Format(string text, int count)
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, count) : text;
}
