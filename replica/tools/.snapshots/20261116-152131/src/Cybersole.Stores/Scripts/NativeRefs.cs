namespace Cybersole.Stores.Scripts;

/// <summary>
/// The native references, taken before anything replaces them (R187).
///
/// <para>
/// Read straight out of the target's own script, at byte offset <c>0x03d05776</c> — the sixth statement of the
/// injecting IIFE, before a single patch:
/// </para>
///
/// <code>
/// const nativeToString = Function.prototype.toString;      // 0x03d05639
/// const nativeOwnNames = Object.getOwnPropertyNames;       // 0x03d05776
/// </code>
///
/// <para>
/// <b>Why it is a step of its own.</b> The key-order layer is installed at <c>0x03d1efd4</c> and the prunes come after
/// it (<c>NAV_PRUNE</c> at <c>0x03d208ca</c>, <c>GLOBAL_PRUNE</c> at <c>0x03d272d4</c>, <c>DOCUMENT_PRUNE</c> at
/// <c>0x03d27858</c>). The prunes enumerate the realm with <c>nativeOwnNames</c>, not with
/// <c>Object.getOwnPropertyNames</c> — so the wrapper sitting upstream of them changes nothing. The replica read the
/// live builtin instead, which made every prune's behaviour depend on whether the wrapper had been installed yet:
/// a wrapper first would have filtered the main-frame names out of the enumeration the prune was about to judge.
/// Holding the reference is what makes the order irrelevant, and the order in the target is the order worth copying.
/// </para>
/// </summary>
public static class NativeRefs
{
    /// <summary>The two references the target holds, in the order it holds them.</summary>
    public static readonly string[] Held = { "toString", "getOwnPropertyNames" };

    /// <summary>The global the reference is published under, so a later body can reach it.</summary>
    public const string OwnNamesGlobal = "__nativeOwnNames";

    /// <summary>One statement, first in the surface.</summary>
    public static string BodyJs() => """
        // ---- the native references (R187) ------------------------------------------------
        // Taken before anything is replaced, exactly where the target takes them: `nativeToString` at 0x03d05639
        // and `nativeOwnNames` at 0x03d05776, six statements into the IIFE. Every prune below enumerates with this
        // reference rather than with the live builtin, which is why the target can install the key-order wrapper
        // ABOVE the prunes and still have them see the honest list.
        try {
          G.__nativeOwnNames = Object.getOwnPropertyNames;
        } catch (e) {}
        """;

    /// <summary>What holding the reference buys.</summary>
    public const string Rule =
        "a captured native reference is what makes the install order irrelevant — the target wraps the enumerator "
        + "above three prunes that enumerate with it";
}
