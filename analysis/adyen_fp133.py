import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Payments\AdyenGateway.cs"
t = io.open(p, encoding="utf-8").read()

old = '''            ["browserInfo"] = new JObject
            {
                ["userAgent"] = c.Session.UserAgent ?? "Mozilla/5.0",
                ["acceptHeader"] = "*/*",
                ["language"] = "en-US",
                ["colorDepth"] = 24,
                ["screenHeight"] = 1080,
                ["screenWidth"] = 1920,
                ["timeZoneOffset"] = 0,
                ["javaEnabled"] = false,
            },
            ["threeDS2RequestData"] = new JObject { ["threeDSCompInd"] = "Y" },'''

new = '''            // R133: the browser profile comes from the same fingerprint the page reported. These were
            // hardcoded to 24 / 1080 / 1920 / offset 0, which is the one thing a 3-D Secure risk engine
            // checks first: a payment whose screen disagrees with the browser that made it is rejected
            // in a way that looks exactly like a declined card.
            ["browserInfo"] = BrowserInfo(c),
            ["threeDS2RequestData"] = new JObject
            {
                ["threeDSCompInd"] = DlpaProfile.From(FingerprintFor(c), TimeZoneOffset(c)).ThreeDsCompInd,
            },'''

if old not in t:
    raise SystemExit("browserInfo block not found")
t = t.replace(old, new, 1)

# helpers, appended before the closing brace of the class
helpers = '''
    /// <summary>
    /// The fingerprint this session's browser reports. Taken from the flow's profile key when the
    /// browser bridge set one, otherwise derived from the User-Agent — never invented per call.
    /// </summary>
    private static Scripts.BrowserFingerprint FingerprintFor(FlowContext c)
    {
        var key = c.Session.Vars.TryGetValue("browser.fingerprintKey", out var stored) && !string.IsNullOrEmpty(stored)
            ? stored
            : c.Session.UserAgent ?? "Mozilla/5.0";
        return Scripts.BrowserFingerprint.ForProfile(key);
    }

    /// <summary>Minutes east of UTC, from the session when the browser reported one.</summary>
    private static int TimeZoneOffset(FlowContext c) =>
        c.Session.Vars.TryGetValue("browser.timezoneOffsetMinutes", out var raw)
        && int.TryParse(raw, System.Globalization.NumberStyles.Integer,
            System.Globalization.CultureInfo.InvariantCulture, out var minutes)
            ? minutes
            : 0;

    /// <summary>
    /// Adyen's <c>browserInfo</c>, derived from the fingerprint so it cannot contradict the page.
    /// The DLPA profile is the same device seen by the scheme, which is why both are built here.
    /// </summary>
    private static JObject BrowserInfo(FlowContext c)
    {
        var fingerprint = FingerprintFor(c);
        var dlpa = Scripts.DlpaProfile.From(fingerprint, TimeZoneOffset(c), c.Session.UserAgent);

        return new JObject
        {
            ["userAgent"] = c.Session.UserAgent ?? "Mozilla/5.0",
            ["acceptHeader"] = "*/*",
            ["language"] = dlpa.BrowserLanguage,
            ["colorDepth"] = fingerprint.ColorDepth,
            ["screenHeight"] = fingerprint.ScreenHeight,
            ["screenWidth"] = fingerprint.ScreenWidth,
            ["timeZoneOffset"] = TimeZoneOffset(c),
            ["javaEnabled"] = false,
        };
    }
'''

idx = t.rstrip().rfind("}")
t = t[:idx] + helpers + "\n" + t[idx:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("browserInfo derives from the fingerprint")
