using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The mobile navigator the image installs, read from its own <c>const NAV</c> capture in R157 — and the one
/// gate that makes it matter.
///
/// <code>
/// const NAV = {"standalone": false, "hardwareConcurrency": 4, "webdriver": false, "maxTouchPoints": 5,
///              "cookieEnabled": true, "appCodeName": "Mozilla", "appName": "Netscape",
///              "appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15…"}
/// </code>
///
/// <para>
/// The phone this describes is an <b>iPhone on iOS 27.0.1</b> with four cores and five touch points. The replica's
/// mobile surface installed screen geometry, the viewport and the Screen shape, and then left
/// <c>maxTouchPoints</c> at whatever Chromium reported — so a page could read a phone's screen from a device that
/// claims no touch screen.
/// </para>
///
/// <para>
/// The gate is the reason that matters, and the image's own comment names it (0x03d27ea7):
/// </para>
///
/// <code>
/// // hsw gates its whole worker path on one of them:
/// //   aK_ = ('ontouchstart' in window);  lK = uS &amp;&amp; aK_ &amp;&amp; &lt;ua not Safari-shaped&gt;;
/// //   QW = nW || lK
/// // With aK_ false the gate opens and we …
/// </code>
///
/// <para>
/// So <c>'ontouchstart' in window</c> is not decoration: one branch of a bot wall's worker path depends on it, and
/// the pair (<c>aK_</c>, user agent shape) decides which branch runs. A profile that claims an iPhone and answers
/// <c>false</c> is answering a question the wall asked in order to choose.
/// </para>
/// </summary>
public static class MobileNavigator
{
    /// <summary>Five touch points, from the capture.</summary>
    public const int MaxTouchPoints = 5;

    /// <summary>Four cores, from the capture.</summary>
    public const int HardwareConcurrency = 4;

    /// <summary>The iOS version the captured profile claims.</summary>
    public const string IosVersion = "27.0.1";

    /// <summary>The touch event handler properties the capture lists on the window.</summary>
    public static readonly IReadOnlyList<string> TouchHandlers = new[]
    {
        "ontouchstart", "ontouchmove", "ontouchend", "ontouchcancel", "ontouchforcechange",
    };

    /// <summary>
    /// The navigator members the capture fixes, in the capture's own order (R159).
    ///
    /// <code>
    /// {"standalone": false, "hardwareConcurrency": 4, "webdriver": false, "maxTouchPoints": 5,
    ///  "cookieEnabled": true, "appCodeName": "Mozilla", "appName": "Netscape",
    ///  "appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15
    ///                 (KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1",
    ///  "platform": "iPhone", "product": "Gecko", "productSub": "20030107",
    ///  "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 …)",
    ///  "vendor": "Apple Computer, Inc.", "vendorSub": "",
    ///  "language": "nl-NL", "onLine": true, "pdfViewerEnabled": true}
    /// </code>
    ///
    /// <para>
    /// Two details are worth naming. <c>vendor</c> is Apple's even though the build string says
    /// <c>CriOS/156.0.8078.54</c> — Chrome on iOS, which is still WebKit, so the vendor stays Apple. And
    /// <c>appVersion</c> is the user agent with <c>Mozilla/</c> removed, exactly: the two are one value, and a
    /// profile that reports them differently is contradicting itself.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> Captured =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["standalone"] = "false",
            ["hardwareConcurrency"] = "4",
            ["webdriver"] = "false",
            ["maxTouchPoints"] = "5",
            ["cookieEnabled"] = "true",
            ["appCodeName"] = "Mozilla",
            ["appName"] = "Netscape",
            ["appVersion"] = "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15 " +
                             "(KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1",
            ["platform"] = "iPhone",
            ["product"] = "Gecko",
            ["productSub"] = "20030107",
            ["vendor"] = "Apple Computer, Inc.",
            ["vendorSub"] = "",
            ["language"] = "nl-NL",
            ["onLine"] = "true",
            ["pdfViewerEnabled"] = "true",
        };

    /// <summary>The Chrome-on-iOS build the captured profile carries, which is still WebKit underneath.</summary>
    public const string CriOsBuild = "156.0.8078.54";

    /// <summary>
    /// The enumeration order the capture lists — 49 names, which <c>for in</c> over navigator walks in exactly
    /// this sequence. Order is itself a fingerprint, so a re-seat has to preserve it.
    /// </summary>
    public static readonly IReadOnlyList<string> NavOrder = new[]
    {
        "standalone", "hardwareConcurrency", "gpu", "clipboard", "audioSession", "credentials",
        "geolocation", "mediaCapabilities", "mediaSession", "mediaDevices", "permissions", "wakeLock",
        "locks", "webdriver", "maxTouchPoints", "userActivation", "cookieEnabled", "appCodeName",
        "appName", "appVersion", "platform", "product", "productSub", "userAgent", "vendor",
        "vendorSub", "language", "languages", "onLine", "plugins", "mimeTypes", "pdfViewerEnabled",
        "serviceWorker", "storage", "sendBeacon", "requestMediaKeySystemAccess", "getGamepads",
        "javaEnabled", "canShare", "share", "toString", "toLocaleString", "valueOf", "hasOwnProperty",
        "propertyIsEnumerable", "isPrototypeOf", "__defineGetter__", "__defineSetter__",
        "__lookupGetter__", "__lookupSetter__",
    };

    /// <summary>The set the capture compares against, one entry longer than the order (51 here, 49 there).</summary>
    public static int NavKeyCount => NavOrder.Count + 2;

    /// <summary>
    /// The wall's branch, in its own terms: <c>aK_</c> is the touch test, <c>lK</c> is the pair
    /// (touch &amp;&amp; a Safari-shaped agent), and <c>QW</c> is the branch that runs.
    /// </summary>
    public const string HswGate =
        "aK_ = ('ontouchstart' in window); lK = uS && aK_ && <ua not Safari-shaped>; QW = nW || lK";

    /// <summary>The consequence the image wrote down.</summary>
    public const string HswConsequence = "with aK_ false the gate opens";

    /// <summary>
    /// <c>history.length</c> is read by the payload and never written: the pool has no <c>pushState</c> or
    /// <c>replaceState</c> at all, so the sample's 9 is whatever the browser had (R157).
    /// </summary>
    public const string HistoryLength = "window.history.length";

    /// <summary>True when the capture fixes this navigator member.</summary>
    public static bool IsCaptured(string? member) =>
        !string.IsNullOrEmpty(member) && Captured.ContainsKey(member);

    /// <summary>
    /// The touch surface a profile must answer: five points and the five handlers when it claims an iPhone,
    /// and nothing at all when it does not.
    /// </summary>
    public static bool ShouldInstallTouches(string? userAgent) =>
        BrowserFingerprintUa.IsApple(userAgent);

    /// <summary>
    /// The statements the mobile body installs for a phone profile — every field the capture fixes, plus the
    /// enumeration order (R159).
    ///
    /// <para>
    /// <c>appVersion</c> is derived rather than hard-coded: it is the user agent with <c>Mozilla/</c> removed, which
    /// is exactly what the capture shows. A profile that reports a hard-coded appVersion while sending a different
    /// agent is contradicting itself in two adjacent properties.
    /// </para>
    /// </summary>
    public static string BodyJs(string? userAgent)
    {
        var language = Captured["language"];

        var js = """
                 try {
                   const N = G.navigator;
                   if (N) {
                     // R164: the image installs these on Navigator.prototype, not on the instance. A detector can
                     // read either, but `Object.getOwnPropertyNames(navigator)` answers differently, and the
                     // capture is written as `Object.keys(NAV).forEach((key) => value(Navigator.prototype, key, …))`.
                     const P = Object.getPrototypeOf(N);
                     // R164: try the prototype first, then the instance, and verify by reading back. A
                     // defineProperty can be accepted and still be ineffective — the browser's own accessor may
                     // answer from the instance — so the check is the read, not the absence of a throw.
                     const put = (name, v) => {
                       const targets = [P, N];
                       for (var i = 0; i < targets.length; i++) {
                         const target = targets[i];
                         if (!target) continue;
                         try {
                           Object.defineProperty(target, name,
                             { value: v, writable: true, configurable: true, enumerable: true });
                           if (N[name] === v) return;
                         } catch (e) {}
                       }
                     };

                     put('maxTouchPoints', __TOUCH__);
                     put('standalone', false);
                     put('cookieEnabled', true);
                     put('appCodeName', 'Mozilla');
                     put('appName', 'Netscape');
                     put('platform', 'iPhone');
                     put('product', 'Gecko');
                     put('productSub', '20030107');
                     put('vendor', 'Apple Computer, Inc.');
                     put('vendorSub', '');
                     put('onLine', true);
                     put('pdfViewerEnabled', true);
                     put('language', '__LANGUAGE__');

                     if (!('webdriver' in N)) put('webdriver', false);

                     // appVersion is the agent minus Mozilla/ — one value, two properties
                     const ua = N.userAgent || '';
                     if (ua) put('appVersion', ua.indexOf('Mozilla/') === 0 ? ua.slice(8) : ua);

                     // R164: languages is ONE element, frozen. The image writes
                     //   value(Navigator.prototype, 'languages', Object.freeze([NAV.language]))
                     // — a phone with a single language, not the usual two-element list.
                     try {
                       const list = Object.freeze(['__LANGUAGE__']);
                       [P, N].forEach((target) => {
                         if (!target) return;
                         try {
                           Object.defineProperty(target, 'languages',
                             { value: list, writable: false, configurable: true, enumerable: true });
                         } catch (e) {}
                       });
                     } catch (e) {}
                   }
                 } catch (e) {}

                 // R196: the five touch handlers used to be installed HERE as `{ value: null, writable: true }`.
                 // The target is explicit that an event-handler IDL attribute is an ACCESSOR pair and that a null data
                 // slot "answers the descriptor probes with a shape no engine gives a handler" — hsw reads .value AND
                 // .get of each descriptor and the getter's source. HandlerSurface installs the pairs now; this body
                 // keeps only the navigator figures.
                 """
            .Replace("__TOUCH__", MaxTouchPoints.ToString())
            .Replace("__LANGUAGE__", language);

        return js;
    }
}

/// <summary>The agent test the two surfaces share, so neither re-implements it.</summary>
public static class BrowserFingerprintUa
{
    /// <summary>True when the agent claims an Apple device or a plain Safari.</summary>
    public static bool IsApple(string? userAgent) => MobileSurface.IsAppleUserAgent(userAgent);
}
