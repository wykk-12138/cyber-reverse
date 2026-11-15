using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The WebAssembly fingerprint, ported from the image's own injected script in R146 — comments and all.
///
/// <para>
/// The original's stealth script carries this block, verbatim in the pool:
/// </para>
///
/// <code>
/// // The challenge frame fingerprints WebAssembly directly. Its payload carries
/// //   ws[0] = [WebAssembly, Module.prototype, Instance.prototype, Memory.prototype, Table.prototype]
/// //              .map((o) => Object.getOwnPropertyNames(o).length)
/// // which Blink answers [19,1,2,5,5] and both iPhones that passed answer [16,1,2,6,6]. The gap is
/// // two features pointing in opposite directions: Chrome ships JSPI (Suspending, promising,
/// // SuspendError) which Safari does not, and Safari ships WebAssembly type reflection
/// // (Memory.prototype.type, Table.prototype.type) which Chrome does not. Dropping three and adding
/// // two lands on the device's numbers exactly. Only the counts are transmitted, but a type() that
/// // threw when called would be a worse answer than one returning the shape the proposal describes.
/// </code>
///
/// <para>
/// Three things make this worth porting rather than paraphrasing. The <b>numbers</b> are a measured
/// fact about two engines. The <b>asymmetry</b> is the whole point: the fix is not "hide WebAssembly",
/// it is "make the count match the device the profile claims". And the last sentence is a design rule
/// worth keeping — <b>a stub that throws is a worse answer than one that returns the shape the proposal
/// describes</b>, because a throwing method is itself a signal.
/// </para>
///
/// <para>
/// The replica's injected script patches navigator, screen and WebGL. It never touched WebAssembly, so
/// a challenge frame asking this one question saw a desktop Chrome claiming to be whatever the profile
/// said while answering Blink's numbers — a contradiction the original had already solved.
/// </para>
/// </summary>
public static class WebAssemblySurface
{
    /// <summary>The five objects counted, in the order the payload counts them.</summary>
    public static readonly IReadOnlyList<string> Counted =
        new[] { "WebAssembly", "Module.prototype", "Instance.prototype", "Memory.prototype", "Table.prototype" };

    /// <summary>What Blink (Chrome/Edge) answers.</summary>
    public static readonly IReadOnlyList<int> BlinkCounts = new[] { 19, 1, 2, 5, 5 };

    /// <summary>What both iPhones that passed answered — the Safari shape.</summary>
    public static readonly IReadOnlyList<int> SafariCounts = new[] { 16, 1, 2, 6, 6 };

    /// <summary>Chrome's JSPI surface, which Safari does not have. Three names to remove.</summary>
    public static readonly IReadOnlyList<string> JspiNames = new[] { "Suspending", "promising", "SuspendError" };

    /// <summary>Safari's type-reflection methods, which Chrome does not have. Two to add.</summary>
    public static readonly IReadOnlyList<string> TypeReflectionMethods = new[] { "type", "type" };

    /// <summary>Where the two added methods go.</summary>
    public static readonly IReadOnlyList<string> TypeReflectionTargets =
        new[] { "Memory.prototype", "Table.prototype" };

    /// <summary>
    /// The rule the original states and this class keeps: a stub must answer, not throw.
    /// </summary>
    public const string StubRule =
        "a type() that threw when called would be a worse answer than one returning the shape the " +
        "proposal describes";

    /// <summary>How many names move to turn Blink's shape into Safari's.</summary>
    public static int Delta =>
        JspiNames.Count + TypeReflectionMethods.Count;

    /// <summary>
    /// True when the first count moves by exactly the names removed.
    ///
    /// <para>
    /// Blink answers 19 and Safari 16, and the three JSPI names are what Blink has extra. The two added
    /// methods land on <c>Memory.prototype</c> and <c>Table.prototype</c>, whose counts go 5 → 6, so the
    /// first vector is untouched by them. The arithmetic has to respect that direction, which is what
    /// R146's first attempt got wrong.
    /// </para>
    /// </summary>
    public static bool CountsDifferByTheDelta =>
        BlinkCounts[0] - SafariCounts[0] == JspiNames.Count
        && SafariCounts[3] - BlinkCounts[3] == 1
        && SafariCounts[4] - BlinkCounts[4] == 1;

    /// <summary>
    /// True when the supplied user agent claims a WebKit engine, which is the only case where this patch
    /// is honest: the counts below are Blink's real numbers, so a profile that claims Chromium needs
    /// nothing done to it (R148).
    /// </summary>
    public static bool ShouldPatch(string? userAgent)
    {
        if (string.IsNullOrEmpty(userAgent)) return false;

        // iPhone/iPad, and desktop Safari which also reports Version/… Safari/…
        if (userAgent.Contains("iPhone", System.StringComparison.OrdinalIgnoreCase)
            || userAgent.Contains("iPad", System.StringComparison.OrdinalIgnoreCase)) return true;

        return userAgent.Contains("Safari", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chrome", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chromium", System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// The statements, without a wrapper — for a caller that needs to place them inside a larger function
    /// such as the bridge's per-realm <c>apply</c>.
    /// </summary>
    public static string BodyJs()
    {
        var js = string.Empty;
        js += "  if (!G.WebAssembly) return;\n";
        js += "  const W = G.WebAssembly;\n";
        js += "  [" + string.Join(", ", JspiNames.Select(n => "\"" + n + "\"")) + "]\n";
        js += "    .forEach((name) => { try { delete W[name]; } catch (e) {} });\n";
        js += "  const addMethod = (target, name, impl) => {\n";
        js += "    if (!target || name in target) return;\n";
        js += "    const fn = function () { return impl.apply(this, arguments); };\n";
        js += "    Object.defineProperty(fn, 'name', { value: name, configurable: true });\n";
        js += "    Object.defineProperty(fn, 'length', { value: 0, configurable: true });\n";
        js += "    Object.defineProperty(target, name,\n";
        js += "      { value: fn, writable: true, configurable: true, enumerable: false });\n";
        js += "  };\n";
        js += "  if (W.Memory) addMethod(W.Memory.prototype, 'type', function () { return { kind: 'memory' }; });\n";
        js += "  if (W.Table) addMethod(W.Table.prototype, 'type', function () { return { kind: 'table' }; });\n";
        return js;
    }

    /// <summary>
    /// The JavaScript that turns Blink's surface into Safari's, in the shape the image uses: delete the
    /// three JSPI names, add two non-enumerable methods whose bodies answer rather than throw.
    /// </summary>
    public static string ToJavaScript()
    {
        var js = string.Empty;
        js += "(function () {\n";
        js += "  const G = window;\n";
        js += "  if (!G.WebAssembly) return;\n";
        js += "  const W = G.WebAssembly;\n";
        js += "  [" + string.Join(", ", JspiNames.Select(n => "\"" + n + "\"")) + "]\n";
        js += "    .forEach((name) => { try { delete W[name]; } catch (e) {} });\n";
        js += "  const addMethod = (target, name, impl) => {\n";
        js += "    if (!target || name in target) return;\n";
        js += "    const fn = function () { return impl.apply(this, arguments); };\n";
        js += "    Object.defineProperty(fn, 'name', { value: name, configurable: true });\n";
        js += "    Object.defineProperty(fn, 'length', { value: 0, configurable: true });\n";
        js += "    Object.defineProperty(target, name,\n";
        js += "      { value: fn, writable: true, configurable: true, enumerable: false });\n";
        js += "  };\n";
        js += "  if (W.Memory) addMethod(W.Memory.prototype, 'type', function () { return { kind: 'memory' }; });\n";
        js += "  if (W.Table) addMethod(W.Table.prototype, 'type', function () { return { kind: 'table' }; });\n";
        js += "})();\n";
        return js;
    }
}
