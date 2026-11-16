namespace Cybersole.Stores.Scripts;

/// <summary>
/// SvelteKit product pages — the third AddToCart gap, and the one whose mechanism is most completely recovered.
///
/// <para>
/// R936. Astro gave an attribute prefix and a method family; Svelte gives the calls. Five literals:
/// </para>
///
/// <code>
/// /__data.json?x-sveltekit-invalidated=001   the data endpoint and its query
/// __sveltekit                                a nonce cookie prefix
/// x-sveltekit-pathname                       a request header
/// x-sveltekit-search                         a request header
/// SvelteKitData                              a type name
/// </code>
///
/// <para>
/// Together they describe the mechanism exactly: a SvelteKit page's data lives at the route's own path plus
/// <c>/__data.json</c>, the request names the route and its query in two headers rather than in the URL, and the
/// <c>invalidated</c> counter says which generation of cached data the client already has. That last one is why the
/// literal carries <c>=001</c> rather than a bare parameter: it is a value, and a request with the wrong one gets stale
/// or re-sent data.
/// </para>
///
/// <para>
/// <b>Why the headers exist.</b> A SvelteKit route can be reached at any path, and the data endpoint is relative to the
/// page that asked for it. Putting the route in headers rather than in the URL means one endpoint serves every route and
/// the server decides what to render from the headers — which is also why a request that omits them cannot be answered
/// correctly, so both are required here rather than optional.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The meaning of the <c>invalidated</c> value beyond being a generation counter, and whether a
/// fresh session should send <c>001</c>. The literal's value is reproduced as a default because it is what the image
/// carries, and the parameter is exposed so a caller that knows better can set it — but nothing recovered says how the
/// counter advances, so no logic here pretends to compute it.
/// </para>
/// </summary>
public static class SvelteKitSurface
{
    internal const string DataPath = "/__data.json";

    /// <summary>The endpoint with the query the image carries, verbatim.</summary>
    internal const string DataEndpoint = "/__data.json?x-sveltekit-invalidated=001";

    internal const string InvalidatedParam = "x-sveltekit-invalidated";

    /// <summary>The cookie prefix SvelteKit uses for its session nonce.</summary>
    internal const string NonceCookiePrefix = "__sveltekit";

    internal const string PathnameHeader = "x-sveltekit-pathname";
    internal const string SearchHeader = "x-sveltekit-search";

    /// <summary>The methods the image names for this platform, plus the two that serve every platform.</summary>
    internal static readonly string[] MethodFamily =
    {
        "ScrapeProductSvelte", "CheckPriceLimitSvelte", "AddToCartSvelte", "RefreshSession", "DetectStorefront",
    };

    internal const int RecoveredLiteralCount = 5;

    /// <summary>
    /// The data URL for a route.
    ///
    /// <para>
    /// The route's own path precedes <c>/__data.json</c>, since the endpoint is relative to the page. A route of "/" gives
    /// <c>/__data.json</c>; anything else keeps its path, with a trailing slash removed so the join cannot produce a
    /// double slash that a server might treat as a different route.
    /// </para>
    /// </summary>
    public static string DataUrl(string routePath, string invalidated = "001")
    {
        var path = string.IsNullOrEmpty(routePath) || routePath == "/"
            ? string.Empty
            : routePath.TrimEnd('/');
        return path + DataPath + "?" + InvalidatedParam + "=" + Uri.EscapeDataString(invalidated ?? "001");
    }

    /// <summary>
    /// The two headers a data request needs, given the route and its query string.
    ///
    /// <para>
    /// Both are always emitted. The image names both, and a request carrying one but not the other would describe a route
    /// whose query the server cannot see — the exact case the headers exist to prevent.
    /// </para>
    /// </summary>
    public static IReadOnlyDictionary<string, string> DataHeaders(string routePath, string? query = null)
    {
        return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            [PathnameHeader] = string.IsNullOrEmpty(routePath) ? "/" : routePath,
            [SearchHeader] = query == null ? string.Empty : (query.StartsWith("?") ? query : "?" + query),
        };
    }

    /// <summary>
    /// True when a cookie name belongs to SvelteKit's nonce family. The prefix is followed by a route or a hash, so the
    /// test is on the prefix plus a boundary -- a bare prefix match would accept <c>__sveltekitz</c>, which is a different
    /// cookie that merely begins with the same letters.
    /// </summary>
    public static bool IsNonceCookie(string? cookieName)
    {
        if (string.IsNullOrEmpty(cookieName)) return false;

        foreach (var prefix in new[] { NonceCookiePrefix, "__Host-" + NonceCookiePrefix })
        {
            if (!cookieName!.StartsWith(prefix, StringComparison.Ordinal)) continue;
            // either the name is the prefix itself, or the prefix ends at a separator
            if (cookieName.Length == prefix.Length) return true;
            var next = cookieName[prefix.Length];
            if (next == '-' || next == '.' || next == '_') return true;
        }
        return false;
    }

    /// <summary>
    /// True when a document looks like a SvelteKit page: it references the data endpoint or the nonce family. Weak in the
    /// same way as Astro's test — a page can be SvelteKit-rendered with neither visible after hydration.
    /// </summary>
    public static bool LooksLikeSvelteKit(string? html) =>
        !string.IsNullOrEmpty(html) &&
        (html!.Contains(DataPath, StringComparison.Ordinal) ||
         html.Contains(NonceCookiePrefix, StringComparison.Ordinal));
}