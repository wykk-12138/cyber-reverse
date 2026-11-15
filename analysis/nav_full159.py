import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileNavigator.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the full capture, in its own order
old_captured = '''    /// <summary>The navigator members the capture fixes, in its order, with their values as text.</summary>
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
        };'''

new_captured = '''    /// <summary>
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
    public static int NavKeyCount => NavOrder.Count + 2;'''

if old_captured not in t:
    raise SystemExit("captured anchor missing")
t = t.replace(old_captured, new_captured, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the full NAV capture is recorded")
