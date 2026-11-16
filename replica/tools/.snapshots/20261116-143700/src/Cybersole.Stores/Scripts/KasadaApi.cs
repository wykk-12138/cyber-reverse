using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The Kasada API's own request shapes — the half of the "Api" mode the replica never had (R200).
///
/// <para>
/// <see cref="KasadaStrategy"/> records the four modes, the status strings and the per-store version headers. What was
/// missing is <b>what the API path actually asks for</b>: six paths carrying Kasada's script id, plus the query
/// parameter and header names. All ten literals below were read out of the image, and each carries its address so a
/// future round can re-check rather than trust.
/// </para>
///
/// <para>
/// The structure is Kasada's: a two-UUID script id (<c>/149e9513-…/2d206a39-…</c>), then the script itself
/// (<c>ips.js</c>), the fingerprint endpoint (<c>fp</c>), the chaff script (<c>a-4-a/c.js</c> — the one the page loads
/// but whose answer is thrown away) and the configuration document (<c>prop.json</c>). The bare forms exist because the
/// id is also carried in a cookie/param on some stores, so the same call is written with and without the prefix.
/// </para>
/// </summary>
public static class KasadaApi
{
    /// <summary>One path with the address it was read at, so provenance is checkable rather than asserted.</summary>
    public sealed record Literal(string Value, string Address, string What);

    /// <summary>The script id, which every full path carries.</summary>
    public const string ScriptId = "/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3";

    /// <summary>Every path literal, in address order.</summary>
    public static readonly IReadOnlyList<Literal> Paths = new[]
    {
        new Literal(ScriptId, "0x06aabf24", "the script id itself"),
        new Literal(ScriptId + "/", "0x06aabfd4", "the id with a trailing slash, as a prefix"),
        new Literal(ScriptId + "/a-4-a/c.js", "0x06aac084", "the chaff script the page loads and never reads"),
        new Literal(ScriptId + "/fp?x-kpsdk-v=", "0x06aac144", "the fingerprint endpoint"),
        new Literal(ScriptId + "/ips.js?", "0x06aac20c", "the script, by id"),
        new Literal("/fp?x-kpsdk-v=", "0x06ab3db4", "the fingerprint endpoint, unprefixed"),
        new Literal("/ips.js?", "0x06ab464c", "the script, unprefixed"),
        new Literal("/prop.json", "0x06ab5ccc", "the configuration document"),
        new Literal("/prop.json?_=", "0x06ab5cfc", "the same document with a cache-buster"),
    };

    /// <summary>The bare script path, as the image writes it.</summary>
    public static string BareScriptPath => "/ips.js?";

    /// <summary>The script path under the id.</summary>
    public static string ScriptPath => ScriptId + "/ips.js?";

    /// <summary>The fingerprint endpoint, bare and under the id.</summary>
    public static string FingerprintPath => "/fp?x-kpsdk-v=";

    /// <inheritdoc cref="FingerprintPath"/>
    public static string ScriptIdFingerprintPath => ScriptId + "/fp?x-kpsdk-v=";

    /// <summary>The configuration document, with and without a cache-buster.</summary>
    public static string PropPath => "/prop.json";

    /// <inheritdoc cref="PropPath"/>
    public static string PropPathCacheBusted => "/prop.json?_=";

    /// <summary>The version parameter, which rides on both endpoints.</summary>
    public static readonly Literal VersionParam = new("x-kpsdk-v", "0x07186f1c", "the version query parameter");

    /// <summary>The two protocol headers the endpoints belong to.</summary>
    public static readonly IReadOnlyList<Literal> Headers = new[]
    {
        new Literal("x-kpsdk-ct", "0x07186dd4", "the client token header"),
        new Literal("x-kpsdk-cd", "0x07186da4", "the client data header"),
    };

    /// <summary>Everything above, so a provenance test can walk it in one pass.</summary>
    public static IEnumerable<Literal> All =>
        Paths.Concat(new[] { VersionParam }).Concat(Headers);

    /// <summary>The one host the image shows for the script, in a fragment that also names the header.</summary>
    public static readonly Literal ScriptOrigin = new(
        "https:///ips.js?&x-kpsdk", "0x05e9fab0", "the origin is a placeholder in the image — the host is per store at runtime");

    /// <summary>
    /// The host is deliberately absent from the image: this literal has an empty authority
    /// (<c>https:///ips.js</c>), so the store supplies it. That is why the "Api" road has no host to copy — and why
    /// inventing one here would be the one thing this workspace forbids.
    /// </summary>
    public const string HostRule =
        "the authority in `https:///ips.js?&x-kpsdk` is empty: the store supplies the host at runtime, so this workspace "
        + "carries none";
}
