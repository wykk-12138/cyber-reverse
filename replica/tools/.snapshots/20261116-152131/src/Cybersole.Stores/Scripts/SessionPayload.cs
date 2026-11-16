using System.Collections.Generic;
using System.Globalization;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The shape of the session payload the image posts, read verbatim from a captured sample in R152.
///
/// <para>
/// The sample begins:
/// </para>
///
/// <code>
/// {"sid":"9a10c34d-32fa-448a-9198-c61cce83a2d2","tid":"3bd808ffef1b18c53173677cfd6a681da5e2",
///  "_t":"ASaMBHzL7WoRfLL6ekqt4MuLNpqk5pjkxXylexghsjlpjqOuGive8Zl6zR5+Mdn2Noxp53pp+hnDIeYT4eFth1e8XY…",
///  "cf_flags":"1006579","fresh-cookie":"true","cookie-_cc":"ASaMBHzL7WoRfLL6ekqt4MuL",
///  "time-unix-epoch-ms":1778830875801,"time-local":"15-5-2026, 09:41:15",
///  "time-string":"Fri May 15 2026 09:41:15 GMT+0200 (Midden-Europese zomertijd)",
///  "time-tz-offset-minutes":-120,"time-tz-has-dst":"true","time-tz-dst-active":"true",
///  "time-tz-std-offset":-120,"time-tz-fixed-locale-string":"6-3-2014, 07:58:39",
///  "dom-local-tag":"ASaMBHzL7WoRfLL6ekqt4MuL","dom-session-tag":"ASaMBHzL7WoRfLL6ekqt4MuL", …}
/// </code>
///
/// <para>
/// Four things in that head are worth naming. <c>cookie-_cc</c> is the <b>first 24 characters</b> of
/// <c>_t</c>, so the cookie is a truncation of the token rather than an independent value. The three
/// <c>time-tz-*</c> flags plus <c>time-tz-std-offset</c> describe daylight saving as a <b>state machine</b>
/// rather than a single number. <c>time-string</c> carries the browser's own locale name —
/// <i>Midden-Europese zomertijd</i>, Dutch — which no amount of UA spoofing changes, because it comes from
/// the host. And <c>time-tz-fixed-locale-string</c> formats one <b>fixed instant</b> in the host locale, which
/// is the cheapest way to cross-check a claimed timezone against a real one.
/// </para>
///
/// <para>
/// The rest of the payload is a fingerprint: userAgentData brands, the connection quartet, plugins with
/// per-plugin filename/desc, two canvas hashes, a <c>canvas_spoofing</c> counter, a <c>js-errors</c> array,
/// and per-font probes. Two of its keys are <b>not</b> DOM properties at all —
/// <c>navigator.automationEnabled</c> and <c>webdriver_detect</c> — which is how the original reports its own
/// findings next to the readings they came from.
/// </para>
/// </summary>
public static class SessionPayload
{
    /// <summary>The head keys, in the order the sample carries them.</summary>
    public static readonly IReadOnlyList<string> HeadKeys = new[]
    {
        "sid", "tid", "_t", "cf_flags", "fresh-cookie", "cookie-_cc",
        "time-unix-epoch-ms", "time-local", "time-string",
        "time-tz-offset-minutes", "time-tz-has-dst", "time-tz-dst-active", "time-tz-std-offset",
        "time-tz-fixed-locale-string", "dom-local-tag", "dom-session-tag",
    };

    /// <summary>How many characters of <c>_t</c> the <c>cookie-_cc</c> value carries.</summary>
    public const int CookieTagLength = 24;

    /// <summary>The instant whose formatting in the host locale exposes a timezone mismatch.</summary>
    public static readonly System.DateTime FixedLocaleDate = new(2014, 3, 6, 7, 58, 39);

    /// <summary>The sample's <c>time-tz-fixed-locale-string</c>, which is that instant in Dutch.</summary>
    public const string FixedLocaleSample = "6-3-2014, 07:58:39";

    /// <summary>
    /// JavaScript's <c>getTimezoneOffset()</c> is minutes <b>behind</b> UTC, so central European summer time
    /// (+02:00) reports -120. The sample says -120 and its locale name says <i>zomertijd</i>, which is how the
    /// two halves corroborate each other.
    /// </summary>
    public static int GetTimezoneOffsetMinutes(int minutesEastOfUtc) => -minutesEastOfUtc;

    /// <summary>True when the reported offset and the standard offset differ — i.e. daylight saving is on.</summary>
    public static bool IsDaylightActive(int offsetMinutes, int standardOffsetMinutes) =>
        offsetMinutes != standardOffsetMinutes;

    /// <summary>The <c>cookie-_cc</c> rule: a truncation of the token, not an independent value.</summary>
    public static string CookieTagFor(string token) =>
        token.Length <= CookieTagLength ? token : token[..CookieTagLength];

    /// <summary>The <c>cf_flags</c> integer as the sample's string form, for a caller that has the number.</summary>
    public static string CfFlags(int flags) => flags.ToString(CultureInfo.InvariantCulture);

    /// <summary>The sample's own cf_flags, recorded because it is a constant of this build's payload.</summary>
    public const int CfFlagsSample = 1006579;

    /// <summary>
    /// Keys that are the original's <b>own findings</b> rather than DOM readings — the reason a detector
    /// cannot tell them apart from the readings they sit beside.
    /// </summary>
    public static readonly IReadOnlyList<string> ComputedKeys = new[]
    {
        "navigator.automationEnabled", "webdriver_detect", "canvas_spoofing", "js-errors",
    };

    /// <summary>The plugin entries the sample reports, all five carrying the same internal filename.</summary>
    public static readonly IReadOnlyList<string> PluginNames = new[]
    {
        "PDF Viewer", "Chrome PDF Viewer", "Chromium PDF Viewer",
        "Microsoft Edge PDF Viewer", "WebKit built-in PDF",
    };

    /// <summary>The filename every one of them reports.</summary>
    public const string PluginFilename = "internal-pdf-viewer";

    /// <summary>The description every one of them reports.</summary>
    public const string PluginDescription = "Portable Document Format";

    /// <summary>The non-standard screen member the original adds, with the value its sample carries.</summary>
    public const string DarkModeKey = "screen.darkMode.enabled";

    /// <summary>False in the sample: the profile it describes is a light-mode Windows desktop.</summary>
    public const bool DarkModeSample = false;

    /// <summary>The connection quartet, in the sample's order.</summary>
    public static readonly IReadOnlyList<string> ConnectionKeys = new[]
    {
        "navigator.connection.effectiveType", "navigator.connection.rtt",
        "navigator.connection.saveData", "navigator.connection.downlink",
    };
}
