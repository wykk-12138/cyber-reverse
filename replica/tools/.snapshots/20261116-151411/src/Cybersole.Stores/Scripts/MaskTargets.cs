using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The masking pass: which owner holds which patched property, and the statements that mask them all (R161).
///
/// <para>
/// R160 built the mechanism and registered nothing, which is the fifth time this session has produced a working
/// piece with no caller. The list below is the caller: every property the surfaces patch, with the object that
/// owns it. The pass runs <b>last</b>, after every body has installed its patches, because masking a getter that
/// has not been installed yet does nothing.
/// </para>
///
/// <para>
/// The table is data rather than code so a test can walk it: for each row, read the descriptor in a real browser
/// and ask <c>Function.prototype.toString</c> what it says. A row that answers source code is a patch that
/// announces itself.
/// </para>
/// </summary>
public static class MaskTargets
{
    /// <summary>One patched property and the object that owns it.</summary>
    public sealed record Target(string Owner, string Property);

    /// <summary>Every patched getter, by owner.</summary>
    public static readonly IReadOnlyList<Target> Getters = new[]
    {
        new Target("G.navigator", "plugins"),
        new Target("G.navigator", "mimeTypes"),
        new Target("G.navigator", "connection"),
        new Target("G.navigator", "maxTouchPoints"),
        new Target("G.navigator", "hardwareConcurrency"),
        new Target("G.navigator", "deviceMemory"),
        new Target("G.navigator", "webdriver"),
        new Target("G.Element.prototype", "clientWidth"),
        new Target("G.Element.prototype", "clientHeight"),
        new Target("G", "devicePixelRatio"),
        new Target("G", "outerWidth"),
        new Target("G", "outerHeight"),
        new Target("G", "innerWidth"),
        new Target("G", "innerHeight"),
        new Target("G.Screen.prototype", "width"),
        new Target("G.Screen.prototype", "height"),
        new Target("G.Screen.prototype", "darkMode"),
        new Target("G.VisualViewport.prototype", "width"),
        new Target("G.Performance.prototype", "memory"),
        new Target("Object.getPrototypeOf(G.navigator)", "standalone"),
        new Target("Object.getPrototypeOf(G.navigator)", "locks"),
    };

    /// <summary>Every patched function, by owner.</summary>
    public static readonly IReadOnlyList<Target> Functions = new[]
    {
        new Target("G.speechSynthesis", "getVoices"),
        new Target("G.Document.prototype", "createEvent"),
        new Target("G.WebGLRenderingContext.prototype", "getParameter"),
    };

    /// <summary>How many properties the pass covers.</summary>
    public static int Count => Getters.Count + Functions.Count;

    /// <summary>
    /// The statements that mask everything above. Runs after the patches, and never throws.
    /// </summary>
    public static string ApplyJs()
    {
        var js = string.Empty;

        js += "  try {\n";
        js += "    const M = G.__nativeMask;\n";
        js += "    if (M) {\n";

        foreach (var target in Getters)
        {
            js += "      try { M.maskGetter(" + target.Owner + ", '" + target.Property + "'); } catch (e) {}\n";
        }

        foreach (var target in Functions)
        {
            // R162: the arity comes from the platform's signature, not from the shim that replaced it — copying
            // `owner[prop].length` copies the patched function's own length, which is zero for a shim written
            // as `function () {}`.
            var arity = NativeArity.For(target.Property);
            if (arity is null)
                throw new System.InvalidOperationException(
                    "no platform arity recorded for " + target.Property);

            js += "      try {\n";
            js += "        const owner = " + target.Owner + ";\n";
            js += "        if (owner && typeof owner." + target.Property + " === 'function')\n";
            js += "          M.asNative(owner." + target.Property + ", '" + target.Property + "', " +
                  arity.Value + ");\n";
            js += "      } catch (e) {}\n";
        }

        js += "    }\n";
        js += "  } catch (e) {}\n";

        return js;
    }

    /// <summary>The rule this pass exists to keep.</summary>
    public const string Rule =
        "mask last: a getter that has not been installed yet cannot be masked, and a patch with no mask "
        + "still announces itself";
}
