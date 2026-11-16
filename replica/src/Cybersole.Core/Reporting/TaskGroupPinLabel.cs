using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// The task-group context menu's pin entry: one label when the group is pinned, another when it is not.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// <c>sub_1405C52E0</c> in 5.18.32, decompiled via IDA:
///
/// <code>
/// v13 = property(0);                       // guarded read, see below
/// if (v13 &amp;&amp; *(void**)v13 == &amp;unk_144DB79D0 &amp;&amp; *(BYTE*)(v13 + 8))
///     v14 = &amp;off_146EB9D88;              // one label
/// else
///     v14 = &amp;off_146EB9C98;              // the other
/// return format(localise(v14), property(1));   // property(1) is the group name
/// </code>
///
/// The condition has three parts: the read succeeded, the value's type tag is the expected one, and its byte is
/// non-zero. **A type mismatch therefore takes the else branch and behaves as "not pinned".**
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: the three-part condition, the two slots, and that the second property is substituted into the
///     chosen text.
///   Observation: the catalogue holds exactly two <c>TaskGroups.Context</c> entries with a placeholder —
///     "Pin {0}" and "Unpin {0}".
///   Inference (high confidence): non-zero means <em>already pinned</em>, so the label offers the opposite action.
///     A context-menu entry names what clicking it will do, so "Unpin" is shown for a pinned group. The alternative —
///     that the flag means "not pinned" — fits the code equally well and is not excluded.
///   NOT REPRESENTABLE: the type-tag check. In C# the flag has one type, so the branch where the value is of an
///     unexpected type cannot occur. The original degrades to "not pinned" there; the replica has no such case, and
///     this is a real difference between the two that no probe can express.
/// </summary>
public static class TaskGroupPinLabel
{
    /// <summary>
    /// Returns "Unpin {name}" for a pinned group and "Pin {name}" otherwise.
    /// </summary>
    /// <param name="pinned">The group's first property, read as a boolean.</param>
    /// <param name="name">The group's second property.</param>
    /// <param name="copy">Resolves a locale key to its text.</param>
    public static string Describe(bool pinned, string name, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        name ??= string.Empty;

        string key = pinned
            ? "TaskGroups.Context.UnpinFormat"
            : "TaskGroups.Context.PinFormat";

        string text = copy(key);
        return text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, name) : text;
    }
}
