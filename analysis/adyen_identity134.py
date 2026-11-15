import io

# AdyenGateway reads the three keys through BrowserIdentity now, so there is one spelling of each.
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Payments\AdyenGateway.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private static Scripts.BrowserFingerprint FingerprintFor(FlowContext c)
    {
        var key = c.Session.Vars.TryGetValue("browser.fingerprintKey", out var stored) && !string.IsNullOrEmpty(stored)
            ? stored
            : c.Session.UserAgent ?? "Mozilla/5.0";
        return Scripts.BrowserFingerprint.ForProfile(key);
    }'''

new = '''    private static Scripts.BrowserFingerprint FingerprintFor(FlowContext c) =>
        Scripts.BrowserIdentity.Fingerprint(c.Session);'''

if old not in t:
    raise SystemExit("FingerprintFor anchor missing")
t = t.replace(old, new, 1)

old_tz = '''    private static int TimeZoneOffset(FlowContext c) =>
        c.Session.Vars.TryGetValue("browser.timezoneOffsetMinutes", out var raw)
        && int.TryParse(raw, System.Globalization.NumberStyles.Integer,
            System.Globalization.CultureInfo.InvariantCulture, out var minutes)
            ? minutes
            : 0;'''

new_tz = '''    private static int TimeZoneOffset(FlowContext c) =>
        Scripts.BrowserIdentity.TimeZoneOffset(c.Session);'''

if old_tz not in t:
    raise SystemExit("TimeZoneOffset anchor missing")
t = t.replace(old_tz, new_tz, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("gateway uses BrowserIdentity for both reads")
