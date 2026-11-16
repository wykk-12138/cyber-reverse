using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The second readable field: <c>fn.length</c>, and the third: <c>fn.name</c> (R162).
///
/// <para>
/// The image's <c>CRED_SHIM</c> entry is <c>{name: "get", length: 1, src: "…"}</c> — one name, one arity, one
/// source. R161 masked the source and copied the arity from the function it had already replaced, which is the
/// patched one: for a shim written as <c>function () {…}</c> that is zero, and a zero-length
/// <c>Document.prototype.createEvent</c> is a different function from the platform's.
/// </para>
///
/// <para>
/// So the arity comes from the platform's own signature, recorded here by hand from the specifications, and the
/// pass sets it rather than copying it. A getter's name is <c>"get &lt;property&gt;"</c> and its length is zero;
/// that half was already right by accident, which is not the same as being right.
/// </para>
/// </summary>
public static class NativeArity
{
    /// <summary>The platform arity of every function the surfaces replace.</summary>
    public static readonly IReadOnlyDictionary<string, int> Functions =
        new Dictionary<string, int>(System.StringComparer.Ordinal)
        {
            // SpeechSynthesis.getVoices()
            ["getVoices"] = 0,

            // Document.createEvent(type)
            ["createEvent"] = 1,

            // WebGLRenderingContext.getParameter(pname)
            ["getParameter"] = 1,

            // Function.prototype.toString()
            ["toString"] = 0,

            // LockManager.request(name, callback) and LockManager.query()
            ["request"] = 2,
            ["query"] = 0,
        };

    /// <summary>Every getter is zero-arity; recorded so the claim is explicit rather than incidental.</summary>
    public const int GetterArity = 0;

    /// <summary>The name a native getter carries.</summary>
    public static string GetterName(string property) => "get " + property;

    /// <summary>The arity for a function name, or null when the table does not know it.</summary>
    public static int? For(string? name) =>
        string.IsNullOrEmpty(name) ? null : Functions.TryGetValue(name, out var n) ? n : null;

    /// <summary>True when the table covers every function the mask pass registers.</summary>
    public static bool CoversAll() =>
        MaskTargets.Functions.Select(t => t.Property).All(n => Functions.ContainsKey(n));

    /// <summary>The rule: a shim's arity is the platform's, not the shim's own.</summary>
    public const string Rule =
        "copying length from the function you just replaced copies your own shim; the platform's arity is a "
        + "fact about the interface, so it is recorded rather than inferred";
}
