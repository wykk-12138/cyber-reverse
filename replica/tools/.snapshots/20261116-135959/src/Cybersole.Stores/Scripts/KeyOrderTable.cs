using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The key-order layer: three entry points reordered through one function (R180).
///
/// <para>
/// The capture patches <c>Object.getOwnPropertyNames</c>, <c>Object.keys</c> and <c>Reflect.ownKeys</c>, and all three
/// call the same <c>reorder(target, names, enumerableOnly)</c>. Five kinds of rule live inside it:
/// </para>
///
/// <list type="number">
/// <item><b>The global object.</b> Numeric indices first, then the engine's own list, then the names this script added;
/// plus <c>MAIN_FRAME_ONLY</c> — <c>_injected_scroll_helper</c>, <c>_injected_navigation</c> — removed from any
/// non-top frame, because "a frame advertised two names its real counterpart lacks".</item>
/// <item><b><c>CSSStyleDeclaration.prototype</c>.</b> Answered from a recorded list, because "the supported-property
/// list is one of the strongest engine tells there is — the engines do not even agree on the interface".</item>
/// <item><b>A <c>CSSStyleDeclaration</c> instance.</b> Filtered to numeric indices alone. The measurement behind that is
/// the sharpest thing in the block: filtering the instance to the device's vocabulary still produced <b>1505</b> names —
/// the correct 881 followed by 624 duplicates in Blink's order — and "a name list that repeats 624 entries is not a
/// vocabulary difference an obscure device could explain; no engine enumerates a property twice".</item>
/// <item><b>The ORDER table.</b> Rules of <c>{ match, names, drop }</c>; <c>wanted.concat(extra)</c>, where <c>drop</c>
/// removes engine members the device does not have and that cannot be deleted.</item>
/// <item><b>Symbols.</b> <c>OrdinaryOwnPropertyKeys</c> puts symbols last, so the string half is reordered and the
/// symbols appended back. The older guard bailed out of any symbol-bearing object — and every interface prototype
/// carries <c>Symbol.toStringTag</c>, so <c>getOwnPropertyNames</c> and <c>Reflect.ownKeys</c> answered differently for
/// the same object, "which is a sharper tell than whatever the rule was hiding".</item>
/// </list>
/// </summary>
public static class KeyOrderTable
{
    /// <summary>One ORDER rule: what it matches, the order it wants, and the names it hides.</summary>
    public sealed record Rule(string Matches, string[] Names, string[] Drop);

    /// <summary>The names the capture strips from every frame but the top one.</summary>
    public static readonly IReadOnlyList<string> MainFrameOnly = new[]
    {
        "_injected_scroll_helper", "_injected_navigation",
    };

    /// <summary>
    /// The recorded orders this workspace keeps. They are NOT in the target's ORDER table: navigator and screen are
    /// ordered by <c>reseat()</c> (<see cref="NavOrder"/>), and the target's table carries Location, Object.prototype,
    /// the three WebAssembly interfaces, the two WebGL surfaces and the three Performance types instead — see
    /// <see cref="KeyOrderRules"/> for those, verbatim.
    /// </summary>
    public static readonly IReadOnlyList<Rule> Rules = new[]
    {
        new Rule("Navigator.prototype", NavOrder.Navigator.ToArray(), NavPrune.BlinkOnly.ToArray()),
        new Rule("Screen.prototype", NavOrder.Screen.ToArray(), new[] { "isExtended", "onchange" }),
    };

    /// <summary>The three entry points the capture patches.</summary>
    public static readonly IReadOnlyList<string> EntryPoints = new[]
    {
        "Object.getOwnPropertyNames", "Object.keys", "Reflect.ownKeys",
    };

    /// <summary>The numeric-index filter a <c>CSSStyleDeclaration</c> instance gets.</summary>
    public const string CssInstanceFilter = "^[0-9]+$";

    /// <summary>The count the capture measured when the filter was looser: the right 881 plus 624 duplicates.</summary>
    public const int MeasuredWithoutFilter = 1505;

    /// <summary>The device's own count for a computed style declaration.</summary>
    public const int DeviceNameCount = 881;

    /// <summary>
    /// Where the dispatch actually lives (R188). This class kept a 150-line <c>BodyJs()</c> that nothing called — the
    /// exact defect this workspace keeps rediscovering ("the call exists, nothing calls it"). The dispatch is
    /// <see cref="WindowOrderWrap.BodyJs"/>, the ORDER table is <see cref="KeyOrderRules.OrderRulesJs"/>, and this
    /// class is now only the measured facts: the frame-only names, the numeric filter, and the two counts.
    /// </summary>
    public const string SupersededBy =
        "WindowOrderWrap.BodyJs() (dispatch) + KeyOrderRules (ORDER table, CSS_DECL) — R188";
    /// <summary>The rule the numeric filter exists for.</summary>
    public const string DuplicateRule =
        "a name list that repeats 624 entries is not a vocabulary difference an obscure device could explain; no engine "
        + "enumerates a property twice";

    /// <summary>Why the symbol guard had to go.</summary>
    public const string SymbolRule =
        "every interface prototype carries Symbol.toStringTag, so bailing out on symbol-bearing objects made "
        + "getOwnPropertyNames and Reflect.ownKeys answer differently for the same object";
}
