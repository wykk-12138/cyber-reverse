using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The device's two window name orders, and what reading them changed (R183).
///
/// <para>
/// The generated half (<see cref="WindowNameTable"/>) holds both lists verbatim: <b>1062</b> names from
/// <c>Object.getOwnPropertyNames(window)</c> and <b>228</b> from <c>Object.keys(window)</c>. The count matters because
/// the previous round recorded 1290 — a number produced by a regex that also caught quoted strings around the array.
/// The list is the evidence; the number was a guess about the list.
/// </para>
///
/// <para>
/// Two facts fall out of comparing them:
/// </para>
///
/// <list type="bullet">
/// <item><b><c>webkit</c> is the last name in the own-names list and absent from the enumerable one.</b> The capture says
/// the iPhone reported <c>["__gCrWeb","hsw","__wdata","webkit"]</c> with <c>webkit</c> <i>last</i>, after two
/// script-created globals — which is only possible if the enumerable pass and the own-names pass put it in different
/// places: "a name reported from the enumerable pass lands BEFORE the script globals and one reported only from the
/// own-names pass lands after them".</item>
/// <item><b>All twelve Chrome-for-iOS names are enumerable.</b> They appear in both lists, so a phone's
/// <c>Object.keys(window)</c> carries them and the two frame-only names are the exception the capture applies itself,
/// not a property of the device.</item>
/// </list>
/// </summary>
public static partial class WindowNameTable
{
    /// <summary>How many names <c>Object.getOwnPropertyNames(window)</c> reports on the device.</summary>
    public static int AllCount => All.Length;

    /// <summary>How many names <c>Object.keys(window)</c> reports on the device.</summary>
    public static int EnumCount => Enum.Length;

    /// <summary>The name that is last in the own-names order and absent from the enumerable one.</summary>
    public const string LastOwnOnly = "webkit";

    /// <summary>The Chrome-for-iOS names, which appear in both orders.</summary>
    public static IReadOnlyList<string> Injected =>
        WindowBaseline.InjectedNames.Where(n => Enum.Contains(n)).ToList();

    /// <summary>Names in the own-names order that the enumerable order does not carry.</summary>
    public static IReadOnlyList<string> OwnOnly =>
        All.Where(n => !Enum.Contains(n)).ToList();

    /// <summary>
    /// The reason both lists are needed: the same name can sit in two different positions, and a page that asks one way
    /// and then the other sees the difference.
    /// </summary>
    public const string Rule =
        "a name reported from the enumerable pass lands BEFORE the script globals and one reported only from the "
        + "own-names pass lands after them";

    /// <summary>The correction this round made to its own earlier number.</summary>
    public const string Correction =
        "1290 was a guess about the list (a regex that also caught quoted strings around the array); the list is 1062";
}
