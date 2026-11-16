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
/// TrustDecision tdfp  trustdevice.js  trustdevice-botd.js  …/tdfp/{de,sg}/{hash}/fm.js
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
        };

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
    /// Every vendor in <see cref="AntiBotVendors"/> that the protocol layer also covers. PerimeterX
    /// is the exception: the image names the vendor and a token, but no <c>_px</c> cookie — so it is
    /// deliberately absent here rather than filled in from memory.
    /// </summary>
    public static IReadOnlyList<string> VendorsWithCookies() => Cookies.Keys.ToList();
}
