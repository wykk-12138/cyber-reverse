using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The reseat: deleting and re-adding a property moves it to the end, so applying the recorded order in sequence
/// leaves the prototype enumerating in that order — for the properties that are <b>configurable</b> (R165).
///
/// <para>
/// The image's mobile script calls a helper named <c>reseat</c> with <c>SCREEN_ORDER</c>, and its navigator block lists
/// <c>NAV_ORDER</c> with the same 49 names in the order <c>for in</c> walked them. Order is a fingerprint: a detector
/// that iterates navigator reads a sequence, and a desktop's sequence is not a phone's.
/// </para>
///
/// <para>
/// One honest limit is built into the mechanism. A non-configurable property cannot be moved at all, so the achieved
/// order is the recorded order <i>restricted to what could be moved</i> — which is why this round measures the result
/// instead of asserting the ideal.
/// </para>
/// </summary>
public static class NavOrder
{
    /// <summary>The statements that reseat an object's own properties into a given order.</summary>
    public static string ReseatBodyJs(IReadOnlyList<string> order)
    {
        var names = string.Join(", ", order.Select(n => "'" + n + "'"));

        return """
               // ---- reseat (R165) ---------------------------------------------------------------
               // Deleting and re-adding a property moves it to the end, so applying the order in sequence
               // leaves the enumerable ones in that order. Non-configurable properties cannot move, and the
               // measurement below says how many that costs.
               try {
                 const target = Object.getPrototypeOf(G.navigator);
                 if (target) {
                   [__ORDER__].forEach((name) => {
                     try {
                       const d = Object.getOwnPropertyDescriptor(target, name);
                       if (!d || !d.configurable) return;
                       delete target[name];
                       Object.defineProperty(target, name, d);
                     } catch (e) {}
                   });
                 }
               } catch (e) {}
               """.Replace("__ORDER__", names);
    }

    /// <summary>The navigator order the capture records.</summary>
    public static IReadOnlyList<string> Navigator => MobileNavigator.NavOrder;

    /// <summary>
    /// The screen order the image reseats with, which is the one its own comment attaches the helper to.
    /// </summary>
    public static IReadOnlyList<string> Screen => MobileSurface.ScreenOrder;

    /// <summary>What the reseat can promise: the order, restricted to the movable properties.</summary>
    public const string Limit =
        "a non-configurable property cannot be moved, so the achieved order is the recorded order restricted to "
        + "what could be moved; the measurement, not the ideal, is what gets asserted";
}
