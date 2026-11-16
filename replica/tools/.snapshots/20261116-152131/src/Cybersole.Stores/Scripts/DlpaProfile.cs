using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Layer 3: the 3-D Secure device profile, derived from the browser fingerprint so the two never
/// contradict each other (R132).
///
/// <para>
/// R131 established that <c>Fingerprint.template.json</c> lives in
/// <c>Cybersole.Helpers.Dlpa</c> and carries the payment scheme's own field spellings —
/// <c>browserColorDepth</c>, <c>browserScreenHeight</c>, <c>browserScreenWidth</c>,
/// <c>browserTZ</c>, <c>browserLanguage</c>, <c>browserUserAgent</c>, <c>browserJavaEnabled</c>,
/// <c>browserJavascriptEnabled</c>, <c>threeDSCompInd</c>, <c>challengeWindowSize</c> — with
/// <b>string</b> values.
/// </para>
///
/// <para>
/// The hard constraint is consistency: a payment whose profile says 1366×768 while the browser
/// reported 1920×1080 is rejected by the scheme's own risk engine, and the rejection is
/// indistinguishable from a declined card. So this class takes a <see cref="BrowserFingerprint"/>
/// and a time zone and <b>derives</b> every field — it never accepts a value that could disagree.
/// </para>
///
/// <para>
/// The one field the payload variant controls is the User-Agent: with
/// <c>fingerprint-v1-sans-ua</c> the caller sends the UA elsewhere, so the profile leaves it out
/// rather than repeating it.
/// </para>
/// </summary>
public sealed record DlpaProfile
{
    /// <summary>The scheme's colour depth, always a string.</summary>
    public string BrowserColorDepth { get; init; } = "24";

    public string BrowserScreenHeight { get; init; } = "1080";
    public string BrowserScreenWidth { get; init; } = "1920";

    /// <summary>Minutes east of UTC, as the scheme spells it (<c>-60</c> is UTC+1).</summary>
    public string BrowserTz { get; init; } = "0";

    public string BrowserLanguage { get; init; } = "en-US";
    public string BrowserJavaEnabled { get; init; } = "false";
    public string BrowserJavascriptEnabled { get; init; } = "true";

    /// <summary>Y when the browser was actually inspected.</summary>
    public string ThreeDsCompInd { get; init; } = "Y";

    /// <summary>Null until a challenge window is chosen; the scheme treats absent and null alike.</summary>
    public string? ChallengeWindowSize { get; init; }

    /// <summary>False until a fingerprint has been submitted for this transaction.</summary>
    public string FingerprintAttempted { get; init; } = "false";

    /// <summary>The User-Agent, omitted for the <c>-sans-ua</c> payload.</summary>
    public string? BrowserUserAgent { get; init; }

    /// <summary>The field order the profile emits, matching the observed literal.</summary>
    public static readonly IReadOnlyList<string> FieldOrder = new[]
    {
        "fingerprintAttempted", "fingerprintData", "challengeWindowSize", "threeDSCompInd",
        "browserJavaEnabled", "browserJavascriptEnabled", "browserLanguage",
        "browserColorDepth", "browserScreenHeight", "browserScreenWidth", "browserTZ",
        "browserUserAgent",
    };

    /// <summary>
    /// Derive the profile from a browser fingerprint. Nothing here can contradict the browser: the
    /// screen, the colour depth and the pixel ratio all come from the same values the page reports.
    /// </summary>
    public static DlpaProfile From(BrowserFingerprint fingerprint, int utcOffsetMinutes,
        string? userAgent = null, string language = "en-US")
    {
        return new DlpaProfile
        {
            BrowserColorDepth = fingerprint.ColorDepth.ToString(CultureInfo.InvariantCulture),
            BrowserScreenHeight = fingerprint.ScreenHeight.ToString(CultureInfo.InvariantCulture),
            BrowserScreenWidth = fingerprint.ScreenWidth.ToString(CultureInfo.InvariantCulture),
            BrowserTz = utcOffsetMinutes.ToString(CultureInfo.InvariantCulture),
            BrowserLanguage = language,
            BrowserJavaEnabled = "false",
            BrowserJavascriptEnabled = "true",
            ThreeDsCompInd = "Y",
            FingerprintAttempted = "false",
            BrowserUserAgent = userAgent,
        };
    }

    /// <summary>
    /// The profile as the scheme receives it: nulls dropped, values stringified.
    ///
    /// <para>
    /// <c>sansUserAgent</c> is the payload variant's decision, not the profile's — it is passed in
    /// rather than re-derived, so one place decides and one place applies.
    /// </para>
    /// </summary>
    public Dictionary<string, string?> ToFields(bool sansUserAgent = false)
    {
        var fields = new Dictionary<string, string?>(System.StringComparer.Ordinal)
        {
            ["fingerprintAttempted"] = FingerprintAttempted,
            ["fingerprintData"] = null,
            ["challengeWindowSize"] = ChallengeWindowSize,
            ["threeDSCompInd"] = ThreeDsCompInd,
            ["browserJavaEnabled"] = BrowserJavaEnabled,
            ["browserJavascriptEnabled"] = BrowserJavascriptEnabled,
            ["browserLanguage"] = BrowserLanguage,
            ["browserColorDepth"] = BrowserColorDepth,
            ["browserScreenHeight"] = BrowserScreenHeight,
            ["browserScreenWidth"] = BrowserScreenWidth,
            ["browserTZ"] = BrowserTz,
        };

        if (!sansUserAgent && BrowserUserAgent is not null)
            fields["browserUserAgent"] = BrowserUserAgent;

        return fields;
    }

    /// <summary>True when this profile agrees with the browser fingerprint it came from.</summary>
    public bool AgreesWith(BrowserFingerprint fingerprint) =>
        BrowserColorDepth == fingerprint.ColorDepth.ToString(CultureInfo.InvariantCulture)
        && BrowserScreenWidth == fingerprint.ScreenWidth.ToString(CultureInfo.InvariantCulture)
        && BrowserScreenHeight == fingerprint.ScreenHeight.ToString(CultureInfo.InvariantCulture);
}
