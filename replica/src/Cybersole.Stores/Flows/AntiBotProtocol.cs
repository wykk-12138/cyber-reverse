using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The <b>protocol layer</b> of the anti-bot systems the 5.18.32 image speaks, read out in R106.
///
/// <para>
/// R105 recorded which vendors the image knows. This records what it actually puts on the wire: the
/// nine <c>x-kpsdk-*</c> Kasada headers, the queue-it join routes, the TrustDevice script names, and
/// the cookies each vendor sets. A flow that recognises a challenge but cannot name its header is
/// still stuck at the challenge.
/// </para>
///
/// <code>
/// Kasada        x-kpsdk-cd ct dt dv fc h im st v          (nine, plus a per-store version)
/// Akamai        _abck  ak_bmsc  ak_bmsc-*
/// DataDome      datadome
/// Cloudflare    cf_clearance
/// Queue-it      queue-it.net  queue-it-set-cookie  panini.queue-it.net
/// TrustDecision tdfp  trustdevice.js  trustdevice-botd.js  …/tdfp/{de,sg}/{hash}/fm.js\n/// PerimeterX    _px3  __pxvid  _pxvid  PerimeterX-Token     (R944, the seventh)
/// </code>
///
/// <para>
/// The two TrustDecision region hashes are worth noting as they are: <c>de/e6058883…
/// and <c>sg/755d8ba8…</c> are per-region script ids, not a version string, so they are recorded
/// verbatim rather than modelled.
/// </para>
/// </summary>
public static class AntiBotProtocol
{
    /// <summary>The nine <c>x-kpsdk-*</c> header names, verbatim.</summary>
    public static readonly IReadOnlyList<string> KasadaHeaders = new[]
    {
        "x-kpsdk-cd", "x-kpsdk-ct", "x-kpsdk-dt", "x-kpsdk-dv", "x-kpsdk-fc",
        "x-kpsdk-h", "x-kpsdk-im", "x-kpsdk-st", "x-kpsdk-v",
    };

    /// <summary>The cookie family per vendor, as the image spells it.</summary>
    public static readonly IReadOnlyDictionary<string, IReadOnlyList<string>> Cookies =
        new Dictionary<string, IReadOnlyList<string>>(System.StringComparer.OrdinalIgnoreCase)
        {
            ["Akamai"] = new[] { "_abck", "ak_bmsc" },
            ["DataDome"] = new[] { "datadome" },
            ["Cloudflare"] = new[] { "cf_clearance" },
            ["Kasada"] = new[] { "kpsdk" },
            // R944: _px3 was recorded as absent in the note below and it is present -- one match in the image. The
            // absence was asserted rather than searched for, which is why it survived. The two visitor ids are kept
            // apart because the image has both spellings and nothing says they hold the same value.
            ["PerimeterX"] = new[] { "_px3", "__pxvid", "_pxvid" },
        };

    /// <summary>
    /// PerimeterX, read out in R944 from its own literals.
    ///
    /// <code>
    /// _px3                 the main cookie
    /// __pxvid · _pxvid     visitor identifiers, double- and single-underscore
    /// PerimeterX-Token     a header, in the capitalisation the image carries
    /// PerimeterXHandler    the handler's name
    /// </code>
    ///
    /// <para>
    /// Two further strings describe behaviour rather than wire format — "Solving PerimeterX" and "PerimeterX block
    /// (Rotating proxy)" — so they are recorded as the image's wording and not interpreted. The second names a rotating
    /// proxy as the remedy for a block, which is a fact about the original's advice rather than about the protocol.
    /// </para>
    /// </summary>
    public static class PerimeterX
    {
        /// <summary>The cookie, as the image spells it.</summary>
        public const string Cookie = "_px3";

        /// <summary>The two visitor identifiers, kept apart because the image has two.</summary>
        public static readonly IReadOnlyList<string> VisitorIds = new[] { "__pxvid", "_pxvid" };

        /// <summary>The header, in the capitalisation the image carries.</summary>
        public const string TokenHeader = "PerimeterX-Token";

        /// <summary>The handler's name, which is how a log line identifies this path.</summary>
        public const string Handler = "PerimeterXHandler";

        /// <summary>The image's own wording, recorded and not interpreted.</summary>
        public static readonly IReadOnlyList<string> Messages = new[]
        {
            "Solving PerimeterX", "PerimeterX block (Rotating proxy)",
        };
    }

    /// <summary>Queue-it's hosts and the cookie it sets.</summary>
    public static readonly IReadOnlyList<string> QueueIt = new[]
    {
        "queue-it.net", ".queue-it.net", "panini.queue-it.net", "queue-it-set-cookie",
    };

    /// <summary>TrustDecision's two scripts and its two per-region fingerprint ids.</summary>
    public static readonly IReadOnlyList<string> TrustDecisionScripts = new[]
    {
        "trustdevice.js", "trustdevice-botd.js", "tdfp",
        "tdfp/de/e6058883d38c943d575ef00c0bc08768/fm.js",
        "tdfp/sg/755d8ba834619d71d88664d0a36c81ce/fm.js",
    };

    /// <summary>True when <paramref name="name"/> is one of the nine Kasada headers.</summary>
    public static bool IsKasadaHeader(string? name) =>
        !string.IsNullOrEmpty(name) && KasadaHeaders.Contains(name, System.StringComparer.Ordinal);

    /// <summary>The cookie a vendor sets, or null when the image names none.</summary>
    public static IReadOnlyList<string>? CookiesFor(string vendor) =>
        Cookies.TryGetValue(vendor, out var list) ? list : null;

    /// <summary>
    /// Every vendor in <see cref="AntiBotVendors"/> that the protocol layer also covers.
    ///
    /// <para>
    /// R944: this used to say PerimeterX was the exception, on the grounds that the image named the vendor and a token but
    /// no <c>_px</c> cookie. That was wrong — <c>_px3</c> is present, one match, and a single search would have shown it.
    /// The comment asserted an absence it had never checked, and the assertion then kept anyone from looking. Every one of
    /// the seven vendors is covered now.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> VendorsWithCookies() => Cookies.Keys.ToList();
}
