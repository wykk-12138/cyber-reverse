using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The three fingerprint layers the image carries, separated in R131 — because R130 put all of them
/// under one name.
///
/// <para>
/// <b>Layer 1 — browser, eight fields, one per profile.</b> The metadata run that lists
/// <c>ColorDepth, DeviceMemory, HardwareConcurrency, PixelRatio, ScreenWidth, ScreenHeight,
/// AvailableScreenWidth, AvailableScreenHeight</c> is a browser surface, and it is what
/// <see cref="BrowserFingerprint"/> materialises per Chrome profile.
/// </para>
///
/// <para>
/// <b>Layer 2 — a named payload with two variants:</b> <c>fingerprint-v1</c> and
/// <c>fingerprint-v1-sans-ua</c>. Two names for one payload differing by the User-Agent is a
/// deliberate choice, not a version number: a caller that already sends the UA elsewhere can ask for
/// the version without it, and a caller that does not wants it included. Both spellings sit in the
/// pool together with <c>fingerPrintToken</c>, <c>fingerprintData</c>, <c>fingerprintHash</c>,
/// <c>fingerprintOutcome</c>, <c>fingerprintResult</c>.
/// </para>
///
/// <para>
/// <b>Layer 3 — the 3-D Secure device profile, and the template file belongs here.</b> The resource is
/// <c>Cybersole.Core … Cybersole.Helpers.Dlpa.Fingerprint.template.json</c> — namespace
/// <c>Dlpa</c>, not a browser namespace. Its payload is a payment-scheme device profile:
/// <c>browserColorDepth</c>, <c>browserScreenHeight</c>, <c>browserScreenWidth</c>, <c>browserTZ</c>,
/// <c>browserLanguage</c>, <c>browserUserAgent</c>, <c>browserJavaEnabled</c>,
/// <c>browserJavascriptEnabled</c>, <c>threeDSCompInd</c>, <c>challengeWindowSize</c>.
/// One observed sample reads <c>browserColorDepth "24"</c>, <c>browserScreenHeight "1440"</c>,
/// <c>browserScreenWidth "5120"</c>, <c>browserTZ "-60"</c>.
/// </para>
///
/// <para>
/// So the profile rotation YG described serves <b>two</b> consumers at once: the anti-bot script wants
/// a browser that looks unique (layer 1/2), and the payment wants a device profile that looks
/// plausible (layer 3). R130 conflated them by calling the template the source of the browser
/// fingerprint. It is not.
/// </para>
/// </summary>
public static class FingerprintLayers
{
    /// <summary>Layer 1's field names, in the order the image lists them.</summary>
    public static IReadOnlyList<string> BrowserFields => BrowserFingerprint.Fields;

    /// <summary>Layer 2's two payload variants.</summary>
    public const string PayloadV1 = "fingerprint-v1";

    /// <inheritdoc cref="PayloadV1"/>
    public const string PayloadV1SansUa = "fingerprint-v1-sans-ua";

    /// <summary>The payload's own field names, seen beside the two variants.</summary>
    public static readonly IReadOnlyList<string> PayloadFields = new[]
    {
        "fingerPrintToken", "fingerprint", "fingerprintData", "fingerprintHash",
        "fingerprintOutcome", "fingerprintResult", "fingerprintAttempted",
    };

    /// <summary>
    /// Layer 3's template resource, fully qualified as the image spells it —
    /// <c>Cybersole.Helpers.Dlpa.Fingerprint.template.json</c>.
    /// </summary>
    public const string DlpaTemplateResource = "Cybersole.Helpers.Dlpa.Fingerprint.template.json";

    /// <summary>Layer 3's field names, in the order the 3-D Secure profile emits them.</summary>
    public static readonly IReadOnlyList<string> DlpaFields = new[]
    {
        "fingerprintAttempted", "fingerprintData", "challengeWindowSize", "threeDSCompInd",
        "browserJavaEnabled", "browserJavascriptEnabled", "browserLanguage",
        "browserColorDepth", "browserScreenHeight", "browserScreenWidth", "browserTZ",
        "browserUserAgent",
    };

    /// <summary>One observed DLPA sample, quoted from the pool, so the shape is on record.</summary>
    public static readonly IReadOnlyDictionary<string, string> DlpaSample =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["browserColorDepth"] = "24",
            ["browserScreenHeight"] = "1440",
            ["browserScreenWidth"] = "5120",
            ["browserTZ"] = "-60",
            ["browserLanguage"] = "en-US",
            ["browserJavascriptEnabled"] = "true",
            ["browserJavaEnabled"] = "false",
            ["threeDSCompInd"] = "Y",
        };

    /// <summary>
    /// Which payload variant a caller wants. A caller that already sends the UA separately asks for
    /// the version without it; anything else wants it included.
    /// </summary>
    public static string PayloadFor(bool userAgentAlreadySent) =>
        userAgentAlreadySent ? PayloadV1SansUa : PayloadV1;

    /// <summary>All three layers, by name — the map R130 was missing.</summary>
    public static readonly IReadOnlyList<string> Layers = new[]
    {
        "browser: 8 fields, one per profile",
        "payload: fingerprint-v1, with or without UA",
        "dlpa: 3-D Secure device profile from Fingerprint.template.json",
    };

    /// <summary>True when the name is one of the two payload variants.</summary>
    public static bool IsPayloadVariant(string? name) =>
        name is PayloadV1 or PayloadV1SansUa;

    /// <summary>The DLPA profile's colour depth is a string, as the scheme expects it.</summary>
    public static string DlpaColorDepth(int bits) => bits.ToString(System.Globalization.CultureInfo.InvariantCulture);
}
