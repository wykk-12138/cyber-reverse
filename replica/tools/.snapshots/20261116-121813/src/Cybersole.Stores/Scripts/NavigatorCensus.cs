using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Where each of the image's fifty navigator names actually lives in this engine, measured in R166 — and what that
/// split means for a replica.
///
/// <para>
/// R165 measured that only 28 of the recorded names are on <c>Navigator.prototype</c>. This round asks where the other
/// twenty-two are, and the answer divides the whole problem in two:
/// </para>
///
/// <code>
/// on Navigator.prototype   27   the engine has them; they need values, not existence
/// on Object.prototype      10   toString, valueOf, hasOwnProperty, __defineGetter__, … — inherited, untouched
/// absent                   13   a phone has them and this engine does not
/// </code>
///
/// <para>
/// The third line is the mirror of <see cref="NavPrune"/> and the reason both lists have to exist. Blink ships members
/// WebKit never had — <c>userAgentData</c>, <c>connection</c>, <c>bluetooth</c> — and those must be <b>deleted</b> for a
/// phone claim. Symmetrically, a phone has members this engine lacks — <c>standalone</c>, <c>credentials</c>,
/// <c>mediaDevices</c>, <c>wakeLock</c>, <c>locks</c>, <c>storage</c>, <c>share</c> — and those must be <b>installed</b>,
/// or the profile is missing exactly the things a mobile page asks for.
/// </para>
///
/// <para>
/// Two of the thirteen are installed here without further work because they are plain values: <c>standalone</c> (a
/// boolean) and <c>locks</c> (an object whose methods a page calls). The rest are deferred by name, and
/// <c>credentials</c> is the largest of them — its shim is a working WebAuthn implementation, which R163 recorded as an
/// open item rather than pretending otherwise.
/// </para>
/// </summary>
public static class NavigatorCensus
{
    /// <summary>Where a recorded name was found.</summary>
    public enum Home
    {
        /// <summary>An own property of <c>Navigator.prototype</c>.</summary>
        Prototype,
        /// <summary>Inherited from <c>Object.prototype</c>.</summary>
        ObjectPrototype,
        /// <summary>Not present at all in this engine.</summary>
        Absent,
    }

    /// <summary>The measured census, name → home, in the recorded order.</summary>
    public static readonly IReadOnlyDictionary<string, Home> Measured = Build();

    /// <summary>The thirteen names a phone has and this engine lacks — the install list.</summary>
    public static IReadOnlyList<string> Missing => Measured
        .Where(kv => kv.Value == Home.Absent)
        .Select(kv => kv.Key).ToList();

    /// <summary>The ten inherited from <c>Object.prototype</c>, which nothing here touches.</summary>
    public static IReadOnlyList<string> Inherited => Measured
        .Where(kv => kv.Value == Home.ObjectPrototype)
        .Select(kv => kv.Key).ToList();

    /// <summary>The names the engine already carries.</summary>
    public static IReadOnlyList<string> Present => Measured
        .Where(kv => kv.Value == Home.Prototype)
        .Select(kv => kv.Key).ToList();

    /// <summary>Names installed as plain values this round.</summary>
    public static readonly IReadOnlyList<string> InstalledNow = new[] { "standalone", "locks" };

    /// <summary>Names deferred, with the reason the reason is not "forgot".</summary>
    public static readonly IReadOnlyDictionary<string, string> Deferred =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["credentials"] = "the image's shim is a working WebAuthn implementation (R163 open item)",
            ["mediaDevices"] = "needs getUserMedia/enumerateDevices surfaces to be believable",
            ["serviceWorker"] = "a navigator.serviceWorker that never registers is itself a tell",
            ["storage"] = "needs estimate() and persisted() answers",
            ["wakeLock"] = "needs request() returning a sentinel with release()",
            ["share"] = "needs canShare/share pair, both callable",
            ["canShare"] = "pair with share",
            ["requestMediaKeySystemAccess"] = "returns a promise about key systems; a stub that resolves nothing is worse",
            ["gpu"] = "WebGPU adapter surface is a fingerprint of its own",
            ["clipboard"] = "needs read/write surfaces",
            ["audioSession"] = "Safari-only; a stub here would be a member Chrome never had either",
        };

    /// <summary>The census, transcribed from the measurement rather than from the capture's prose.</summary>
    private static IReadOnlyDictionary<string, Home> Build()
    {
        var map = new Dictionary<string, Home>(System.StringComparer.Ordinal);

        void Mark(Home home, params string[] names)
        {
            foreach (var name in names) map[name] = home;
        }

        Mark(Home.Prototype,
            "hardwareConcurrency", "geolocation", "mediaCapabilities", "mediaSession", "permissions",
            "webdriver", "maxTouchPoints", "userActivation", "cookieEnabled", "appCodeName", "appName",
            "appVersion", "platform", "product", "productSub", "userAgent", "vendor", "vendorSub",
            "language", "languages", "onLine", "plugins", "mimeTypes", "pdfViewerEnabled",
            "sendBeacon", "getGamepads", "javaEnabled");

        Mark(Home.ObjectPrototype,
            "toString", "toLocaleString", "valueOf", "hasOwnProperty", "propertyIsEnumerable",
            "isPrototypeOf", "__defineGetter__", "__defineSetter__", "__lookupGetter__",
            "__lookupSetter__");

        Mark(Home.Absent,
            "standalone", "gpu", "clipboard", "audioSession", "credentials", "mediaDevices",
            "wakeLock", "locks", "serviceWorker", "storage", "requestMediaKeySystemAccess",
            "canShare", "share");

        return map;
    }

    /// <summary>The rule the two lists make together.</summary>
    public const string Rule =
        "prune what the engine has and a phone lacks; install what a phone has and the engine lacks; the two lists "
        + "are the same measurement read in opposite directions";
}
