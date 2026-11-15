using System.Collections.Generic;
using System.Globalization;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The mobile (iPhone) surface the image's injected script installs, with its reasons — read out of the
/// original's own comments in R147.
///
/// <para>
/// <see cref="WebAssemblySurface"/> came from one block of that script; this is the rest of it, and the
/// comments are worth more than the numbers because each one names a detector that caught a previous
/// attempt:
/// </para>
///
/// <list type="bullet">
/// <item><b>TouchEvent.</b> Blink's <c>Document.createEvent('TouchEvent')</c> throws
/// <c>NotSupportedError</c>, so a page claiming iOS 26 was caught reporting that touch creation failed
/// while <c>'ontouchstart' in window</c>, <c>maxTouchPoints</c> and a <c>TouchEvent</c> constructor all said
/// otherwise <i>in the same payload</i>. Blink keeps the constructor, so the factory's result can be built
/// directly: <c>new TouchEvent('')</c> — type "", empty TouchLists, <c>isTrusted</c> false, not dispatched.</item>
/// <item><b>performance.memory.</b> Blink-only, WebKit never shipped it, and hsw probes
/// <c>"memory" in performance</c>. It lives on <c>Performance.prototype</c>, so neither a window deletion
/// pass nor a navigator prune reaches it.</item>
/// <item><b>Screen shape.</b> Blink's Screen carries <c>isExtended</c> and <c>onchange</c> from Multi-Screen
/// Window Placement; hCaptcha copies <c>for (var k in screen)</c> wholesale and reads both presence and
/// position, so a ten-key screen under an iPhone user agent contradicts the eight keys a real device
/// reports.</item>
/// <item><b>Geometry.</b> Patching <c>outer</c> without <c>inner</c> is worse than patching neither: it
/// manufactures <c>innerWidth &gt; outerWidth</c> and <c>innerWidth &gt; screen.width</c>, neither of which
/// any real browser can produce.</item>
/// <item><b>Frames.</b> The device figures are for the top-level window only. Inside a frame the honest
/// answer is the frame's own box — but a frame that was never shown lays out 0×0, and 0×0 is worse than a
/// wrong-but-plausible figure, so native values are kept only when the frame actually has one.</item>
/// <item><b>The scrollbar tell.</b> hCaptcha pushes
/// <c>[scrollX, scrollY, clientWidth / min(innerWidth, clientWidth), now]</c> into its motion data. With
/// <c>innerWidth</c> spoofed and <c>clientWidth</c> real, the ratio read 1.2437 and then 1.2065 once a
/// Windows scrollbar took 15px — and <b>iOS scrollbars are overlays that never consume layout width</b>,
/// so a ratio that changes on scroll is the unforgeable half. Pinning <c>clientWidth</c> makes it exactly 1
/// and scroll-invariant.</item>
/// </list>
///
/// <para>
/// Two of these are a lesson in themselves. The frame rule says "leave it alone when leaving it alone is
/// more honest", and the scrollbar rule says the tell was not the number but <b>the number changing when it
/// should not</b>.
/// </para>
/// </summary>
public static class MobileSurface
{
    /// <summary>The device the script models: 402×874 with Safari's 190px of chrome.</summary>
    public const int ScreenWidth = 402;
    public const int ScreenHeight = 874;
    public const int ChromeHeight = 190;

    /// <summary>The top-level viewport: the screen minus the browser chrome.</summary>
    public static int ViewportHeight => ScreenHeight - ChromeHeight;

    /// <summary>The three keys a real iPhone screen reports, plus the geometry Blink adds.</summary>
    public static readonly IReadOnlyList<string> ScreenOrder = new[]
    {
        "height", "width", "colorDepth", "pixelDepth", "availLeft", "availTop",
        "availHeight", "availWidth", "orientation",
    };

    /// <summary>Blink-only Screen members that must not survive, because hCaptcha counts keys.</summary>
    public static readonly IReadOnlyList<string> BlinkOnlyScreenMembers = new[] { "isExtended", "onchange" };

    /// <summary>Blink-only APIs the script removes, each with the probe that finds it.</summary>
    public static readonly IReadOnlyDictionary<string, string> Removed =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["Performance.prototype.memory"] = "\"memory\" in performance (hsw)",
            ["TouchEvent from createEvent"] = "createEvent('TouchEvent') throws NotSupportedError in Blink",
        };

    /// <summary>The aliases a WebKit window is expected to carry.</summary>
    public static readonly IReadOnlyList<string> WebKitAliases = new[] { "webkitIndexedDB" };

    /// <summary>The device pixel ratio of the modelled phone.</summary>
    public const int DevicePixelRatio = 3;

    /// <summary>
    /// What <c>createEvent</c> returns for a touch event: an uninitialised one, which
    /// <c>new TouchEvent('')</c> reproduces.
    /// </summary>
    public const string TouchEventFactory = "new TouchEvent('')";

    /// <summary>
    /// The VisualViewport values the image installs, verbatim (R151):
    /// <c>{offsetLeft: 0, offsetTop: 0, pageLeft: 0, pageTop: 0, width: VW, height: VH, scale: 1}</c>.
    ///
    /// <para>
    /// This is the half of the geometry the replica had left alone. The image's comment says the failure it
    /// fixes: "innerWidth/innerHeight and visualViewport were the only geometry left unpatched, so they
    /// reported the real host window while outerWidth/outerHeight reported the device."
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> VisualViewportFields = new[]
    {
        "offsetLeft", "offsetTop", "pageLeft", "pageTop", "width", "height", "scale",
    };

    /// <summary>
    /// <c>orientation</c> is in the shape but <b>not</b> in the image's value object — the native
    /// <c>ScreenOrientation</c> already says portrait for a phone-sized window, so patching it would be a
    /// claim with nothing to correct (R151).
    /// </summary>
    public const string OrientationIsNative = "orientation";

    /// <summary>The two element boxes pinned so the page-zoom ratio cannot move on scroll.</summary>
    public static readonly IReadOnlyList<string> PinnedBoxes = new[] { "clientWidth", "clientHeight" };

    /// <summary>Why the ratio matters, in the original's own terms.</summary>
    public const string ScrollbarTell =
        "iOS scrollbars are overlays and never consume layout width, so a clientWidth/innerWidth ratio " +
        "that changes on scroll cannot come from any iPhone";

    /// <summary>The frame rule: keep the native box when it exists, because 0×0 is worse than a guess.</summary>
    public const string FrameRule =
        "inside a frame the frame's own box is the honest answer; the device figures are for the " +
        "top-level window only";

    /// <summary>A geometry pair that no browser can produce, and which the script avoids by construction.</summary>
    public static bool IsImpossibleGeometry(int innerWidth, int outerWidth, int screenWidth) =>
        innerWidth > outerWidth || innerWidth > screenWidth;

    /// <summary>The page-zoom ratio hCaptcha computes.</summary>
    public static double ZoomRatio(int clientWidth, int innerWidth) =>
        innerWidth == 0 ? 0 : (double)clientWidth / innerWidth;

    /// <summary>Formatting helper so a test can compare against the string the script would emit.</summary>
    public static string Format(double value) =>
        value.ToString("0.####", CultureInfo.InvariantCulture);

    /// <summary>
    /// True when the user agent claims an Apple device, which is the only case where installing the
    /// phone figures is honest (R148).
    ///
    /// <para>
    /// The same rule as <see cref="WebAssemblySurface.ShouldPatch"/>: these numbers describe a 402×874
    /// iPhone, so putting them on a profile that claims a 363×684 desktop window would replace one
    /// incoherence with another. A patch is not a lie to be sprinkled; it is the correction of a specific
    /// mismatch.
    /// </para>
    /// </summary>
    public static bool IsAppleUserAgent(string? userAgent)
    {
        if (string.IsNullOrEmpty(userAgent)) return false;

        if (userAgent.Contains("iPhone", System.StringComparison.OrdinalIgnoreCase)
            || userAgent.Contains("iPad", System.StringComparison.OrdinalIgnoreCase)) return true;

        return userAgent.Contains("Safari", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chrome", System.StringComparison.OrdinalIgnoreCase)
            && !userAgent.Contains("Chromium", System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>
    /// The statements the bridge installs in each realm, without a wrapper.
    ///
    /// <para>
    /// Geometry is applied only when the realm is the top-level window: inside a frame the frame's own box
    /// is the honest answer, and a frame that was never shown lays out 0×0, which is worse than a
    /// wrong-but-plausible figure. Everything else — the Screen shape, the alias, the removals, the touch
    /// factory, the pinned box — applies in every realm, because a challenge frame reads those itself.
    /// </para>
    /// </summary>
    public static string BodyJs()
    {
        var js = string.Empty;

        // G is supplied by the caller's wrapper: both bodies share one realm reference, and declaring it
        // twice in the same function is a syntax error (R149 — the first run of the runtime test caught
        // exactly that, because the surface call is the last statement of apply and its throw was swallowed).
        js += "  const value = (target, name, v) => {\n";
        js += "    try { Object.defineProperty(target, name,\n";
        js += "      { value: v, writable: true, configurable: true, enumerable: true }); } catch (e) {}\n";
        js += "  };\n";

        js += "  const isTop = (() => { try { return G === G.top; } catch (e) { return false; } })();\n";

        // 1. webkitIndexedDB — a WebKit window is expected to carry the alias
        js += "  try { if (!('" + WebKitAliases[0] + "' in G) && G.indexedDB)\n";
        js += "    value(G, '" + WebKitAliases[0] + "', G.indexedDB); } catch (e) {}\n";

        // 2. performance.memory is Blink-only and lives on the prototype, where no prune reaches it
        js += "  try { if (G.Performance && G.Performance.prototype)\n";
        js += "    delete G.Performance.prototype.memory; } catch (e) {}\n";

        // 3. the touch factory must return an event, never throw
        js += "  try {\n";
        js += "    if (G.Document && G.Document.prototype && typeof G.TouchEvent === 'function') {\n";
        js += "      const createEvent = G.Document.prototype.createEvent;\n";
        js += "      G.Document.prototype.createEvent = function (type) {\n";
        js += "        try {\n";
        js += "          if (arguments.length && String(type).toLowerCase() === 'touchevent')\n";
        js += "            return " + TouchEventFactory + ";\n";
        js += "        } catch (e) {}\n";
        js += "        return createEvent.apply(this, arguments);\n";
        js += "      };\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        // 4. the Screen shape: the device's keys, in the device's order, and nothing Blink added
        js += "  try {\n";
        js += "    if (G.Screen && G.Screen.prototype) {\n";
        js += "      const S = G.Screen.prototype;\n";
        js += "      const shape = { width: " + ScreenWidth + ", height: " + ScreenHeight +
              ", availWidth: " + ScreenWidth + ", availHeight: " + ScreenHeight + ",\n";
        js += "        availLeft: 0, availTop: 0, colorDepth: 24, pixelDepth: 24 };\n";
        js += "      Object.keys(shape).forEach((k) => value(S, k, shape[k]));\n";
        js += "      const ORDER = [" + string.Join(", ",
              ScreenOrder.Select(k => "'" + k + "'")) + "];\n";
        js += "      const KEEP = new Set(ORDER);\n";
        js += "      Object.getOwnPropertyNames(S).forEach((k) => {\n";
        js += "        if (!KEEP.has(k) && k !== 'constructor') { try { delete S[k]; } catch (e) {} }\n";
        js += "      });\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        // 5. geometry, top level only — and the pinned box that keeps the zoom ratio scroll-invariant
        // R150: these four are pinned with getters rather than assigned. An assigned value is a plain
        // data property, and the browser re-derives outerHeight when the window is resized — which the
        // host does after the script runs. A getter survives that, and it is also what "the profile says
        // this is the device" means: the page cannot observe anything else.
        js += "  if (isTop) {\n";
        js += "    const pin = (name, v) => {\n";
        js += "      try { Object.defineProperty(G, name, { configurable: true, get: () => v }); } catch (e) {}\n";
        js += "    };\n";
        js += "    const pinAll = () => {\n";
        js += "      pin('devicePixelRatio', " + DevicePixelRatio + ");\n";
        js += "      pin('outerWidth', " + ScreenWidth + ");\n";
        js += "      pin('outerHeight', " + ScreenHeight + ");\n";
        js += "      pin('innerWidth', " + ScreenWidth + ");\n";
        js += "      pin('innerHeight', " + ViewportHeight + ");\n";
        js += "    };\n";
        js += "    pinAll();\n";
        // Chromium installs its own window geometry once the window is realised, which is after
        // document-start — R150 measured exactly that: the accessor was accepted, and 769 was back a
        // moment later. Re-pinning at the three moments the browser settles geometry is what makes the
        // claim stick; the descriptor is configurable, so each re-pin replaces its accessor.
        js += "    ['DOMContentLoaded', 'load', 'resize'].forEach((ev) => {\n";
        js += "      try { G.addEventListener(ev, pinAll); } catch (e) {}\n";
        js += "    });\n";
        js += "  }\n";

        // 6. VisualViewport, top level only — it is the viewport of the window, not of a frame
        js += "  if (isTop) {\n";
        js += "    try {\n";
        js += "      const VV = G.VisualViewport && G.VisualViewport.prototype;\n";
        js += "      if (VV) {\n";
        js += "        const vv = { offsetLeft: 0, offsetTop: 0, pageLeft: 0, pageTop: 0,\n";
        js += "          width: " + ScreenWidth + ", height: " + ViewportHeight + ", scale: 1 };\n";
        js += "        Object.keys(vv).forEach((k) => value(VV, k, vv[k]));\n";
        js += "      }\n";
        js += "    } catch (e) {}\n";
        js += "  }\n";

        // 7. clientWidth/clientHeight on documentElement, in every realm: the ratio must be exactly 1
        js += "  try {\n";
        js += "    if (G.Element && G.Element.prototype) {\n";
        js += "      [['clientWidth', " + ScreenWidth + "], ['clientHeight', " + ViewportHeight + "]]\n";
        js += "        .forEach((pair) => {\n";
        js += "          const name = pair[0], want = pair[1];\n";
        js += "          const original = Object.getOwnPropertyDescriptor(G.Element.prototype, name);\n";
        js += "          if (!original || !original.get) return;\n";
        js += "          Object.defineProperty(G.Element.prototype, name, {\n";
        js += "            configurable: true, enumerable: original.enumerable,\n";
        js += "            set: original.set,\n";
        js += "            get: function () {\n";
        js += "              try {\n";
        js += "                const doc = this.ownerDocument || G.document;\n";
        js += "                if (doc && this === doc.documentElement) return want;\n";
        js += "              } catch (e) {}\n";
        js += "              return original.get.call(this);\n";
        js += "            },\n";
        js += "          });\n";
        js += "        });\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        return js;
    }

    /// <summary>
    /// The engine-level members R156 added: five plugins, the connection quartet, and the image's two
    /// non-standard flags.
    ///
    /// <para>
    /// These are <b>not</b> mobile figures — they are what a real Chromium reports — so this body is installed
    /// for every profile, not gated. The plugin list is five because the sample says
    /// <c>navigator.plugins.count = 5</c> and all five share <c>internal-pdf-viewer</c>; the replica had three,
    /// which a count alone would catch.
    /// </para>
    /// </summary>
    public static string EngineBodyJs()
    {
        var js = string.Empty;

        // 1. plugins and mimeTypes are left NATIVE (R169). The image's own note is decisive: Blink's lists are the
        //    spec's five PDF viewers — all `internal-pdf-viewer` — and two PDF mime types, which is exactly what an
        //    iPhone reports, and the device collector reads lengths 5 / 2. An override used to empty both, on the
        //    mistaken belief that WebKit's lists are empty, so every bot payload carried `plugins: []`.
        //
        //    So the only correct patch here is none. Kept as a comment so the next reader does not add one back.

        // 2. the connection quartet, with the sample's values
        // R169: on the PROTOTYPE, so the whitelist prune can delete it for a phone claim. Installing it on the
        // instance left `connection` visible on an iPhone profile because the prune only walks the prototype — the
        // measurement said so: phone leaves = ["connection","deviceMemory"].
        js += "  try {\n";
        js += "    const P = G.Navigator && G.Navigator.prototype;\n";
        js += "    if (P) {\n";
        js += "      const connection = { effectiveType: '4g', rtt: 50, saveData: false, downlink: 10 };\n";
        js += "      Object.defineProperty(P, 'connection',\n";
        js += "        { get: () => connection, configurable: true, enumerable: true });\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        // 3. the two flags the image reports beside the readings they came from
        js += "  try {\n";
        js += "    if (G.navigator && !('automationEnabled' in G.navigator)) {\n";
        js += "      Object.defineProperty(G.navigator, 'automationEnabled',\n";
        js += "        { value: false, configurable: true, enumerable: true });\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        js += "  try {\n";
        js += "    if (G.Screen && G.Screen.prototype) {\n";
        js += "      const darkMode = Object.freeze({ enabled: " +
              (SessionPayload.DarkModeSample ? "true" : "false") + " });\n";
        js += "      Object.defineProperty(G.Screen.prototype, 'darkMode',\n";
        js += "        { get: () => darkMode, configurable: true, enumerable: true });\n";
        js += "    }\n";
        js += "  } catch (e) {}\n";

        return js;
    }
}
