using System;

namespace Cybersole.Core.Reporting;

/// <summary>
/// Delete confirmations for accounts and account groups.
///
/// WHERE THIS COMES FROM (AGENTS.md §0: decompilation is the primary reference)
/// Two functions that look alike and are not:
///
/// <c>sub_14065EBF0</c> — accounts, decompiled R736:
/// <code>
/// v2 = count;
/// *(DWORD*)(box + 8) = v2;             // boxes an INT32
/// title   = format(&amp;off_146B39F90, box);
/// message = format(&amp;off_146B39F30, box);
/// dialog(title, message, 1);
/// dialog[528] = format(&amp;off_146B39ED0, box);
/// show(dialog);
/// </code>
///
/// <c>sub_1407A8450</c> — account groups, same round:
/// <code>
/// arg = *(QWORD*)(model[8] + 24);      // passes an OBJECT reference, no boxing
/// title   = format(&amp;off_146B3A370, arg);
/// message = format(&amp;off_146B3A300, arg);
/// dialog(title, message, 1);
/// dialog[528] = format(&amp;off_146B3A298, arg);
/// v14 = model[16];
/// if (v14) show(dialog);                // guard is the HOST, not the value
/// </code>
///
/// **Two differences, both behavioural:**
///
/// <list type="number">
/// <item>The substituted value is an account count in one and a group name in the other. The catalogue says the
/// same thing — "delete {0} accounts?" against "delete the {0} account group?" — so the same placeholder carries
/// two different types.</item>
/// <item>The guards differ. The accounts function tests the count; the group function tests whether a host window
/// exists before showing. So the group texts are built <b>unconditionally</b> and merely not displayed when there
/// is no host, while the accounts texts are not built at all for a zero count.</item>
/// </list>
///
/// That second difference is why <see cref="Accounts"/> returns <c>null</c> and <see cref="AccountGroup"/> does not:
/// the contracts are different because the code is different, and a shared helper that gave both the same contract
/// would be wrong for one of them. This is the concrete case R735 warned about when it declined to wire the family
/// on the strength of a shared shape.
///
/// WHAT IS OBSERVED AND WHAT IS INFERRED
///   Observation: both bodies, including the boxing of an int in one and an object reference in the other, and the
///     two different guards.
///   Observation: the six catalogue texts.
///   Inference (high confidence): the slot-to-key assignment, from the dialog builder's argument order established in
///     R732 and consistent across every body read since.
///   Not established: whether a group with an empty name still reaches the show call — the guard is host presence,
///     not name presence, so on this evidence it does.
/// </summary>
public static class AccountDeletePrompts
{
    /// <summary>
    /// The accounts grid's confirmation, or <c>null</c> for a zero selection — the accounts body tests the count and
    /// returns before building anything.
    /// </summary>
    public static (string Title, string Message, string Action)? Accounts(int count, Func<string, string> copy)
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
            Format(copy("Accounts.DeleteConfirm.TitleFormat"), count),
            Format(copy("Accounts.DeleteConfirm.MessageFormat"), count),
            Format(copy("Accounts.DeleteConfirm.ActionFormat"), count));
    }

    /// <summary>
    /// The account-group confirmation. Always returns the texts: the group body guards the <em>show</em> call on a
    /// host, not the construction on the value, so there is no value for which it builds nothing.
    /// </summary>
    public static (string Title, string Message, string Action) AccountGroup(string group, Func<string, string> copy)
    {
        if (copy is null)
        {
            throw new ArgumentNullException(nameof(copy));
        }

        group ??= string.Empty;

        return (
            Format(copy("Accounts.Group.DeleteConfirm.TitleFormat"), group),
            Format(copy("Accounts.Group.DeleteConfirm.MessageFormat"), group),
            Format(copy("Accounts.Group.DeleteConfirm.ActionFormat"), group));
    }

    private static string Format(string text, object arg)
        => text.Contains("{0}", StringComparison.Ordinal) ? string.Format(text, arg) : text;
}
