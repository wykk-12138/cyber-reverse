using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Next.js product pages — the two handles the image carries for reading one.
///
/// <para>
/// R934. The AddToCart work had five platform gaps and Box closed one; Next is the next of them, and unlike Astro or
/// Svelte the image carries two specific literals rather than just the framework's name:
/// </para>
///
/// <code>
/// script#__NEXT_DATA__                                      a CSS selector
/// /_next/static/chunks/app/[^"']*?page-[0-9a-f]+\.js        a regex
/// /_next/                                                   the asset root
/// /pay/_next/                                               a payment page's asset root
/// </code>
///
/// <para>
/// Together they say the mechanism: select the script element by that id and read its JSON, and locate the route's page
/// chunk by matching the app-router filename pattern. The first is how a Next page exposes its own data; the second is
/// how a client finds the chunk that renders the current route, which matters because the build hash is per deployment
/// and cannot be hard-coded.
/// </para>
///
/// <para>
/// <b>What is inference.</b> Nothing about the shape of the JSON beyond it being JSON. <c>__NEXT_DATA__</c> holds a
/// <c>props.pageProps</c> object by convention, and that convention is used to find a product without pretending it was
/// recovered — so the lookup below falls back to a whole-document search and reports which it used. A caller told
/// "found by convention" knows to check; one told "found" does not.
/// </para>
/// </summary>
public static class NextJsSurface
{
    /// <summary>The selector the image names, verbatim.</summary>
    internal const string DataSelector = "script#__NEXT_DATA__";

    /// <summary>The app-router page chunk pattern the image names, verbatim.</summary>
    internal const string PageChunkPattern = @"/_next/static/chunks/app/[^""']*?page-[0-9a-f]+\.js";

    internal const string AssetRoot = "/_next/";
    internal const string PayAssetRoot = "/pay/_next/";

    internal const int RecoveredLiteralCount = 4;

    /// <summary>Where a value was found, because convention and recovery are different kinds of evidence.</summary>
    public enum Found
    {
        /// <summary>Under <c>props.pageProps</c>, where Next puts a page's own data by convention.</summary>
        PageProps,

        /// <summary>Somewhere else in the document. Found, but not where convention says to look first.</summary>
        Elsewhere,

        /// <summary>Not present.</summary>
        Absent,
    }

    /// <summary>
    /// Extracts the JSON from a page's <c>script#__NEXT_DATA__</c> element.
    ///
    /// <para>
    /// The element is matched by its id attribute rather than by position, since a page's script order is not something
    /// the image says anything about. Returns null when the tag or its contents are missing, which is the same answer
    /// for "not a Next page" and "a Next page that did not embed data" — the two are indistinguishable from the HTML
    /// alone and a caller treats both as "look elsewhere".
    /// </para>
    /// </summary>
    public static string? ExtractDataJson(string? html)
    {
        if (string.IsNullOrEmpty(html)) return null;

        // R934: HTML allows an unquoted attribute value, so the value is matched with or without quotes. The first
        // version required quotes and rejected <script id=__NEXT_DATA__>, which is valid HTML that a minifier can
        // produce -- and the test that caught it was written for exactly that reason.
        var m = Regex.Match(html,
            @"<script[^>]*\bid\s*=\s*(?:[""']__NEXT_DATA__[""']|__NEXT_DATA__(?=[\s>/]))[^>]*>(.*?)</script\s*>",
            RegexOptions.Singleline | RegexOptions.IgnoreCase);
        if (!m.Success) return null;

        var json = m.Groups[1].Value.Trim();
        return json.Length == 0 ? null : json;
    }

    /// <summary>
    /// Parses the data and looks for a property, saying where it found it.
    ///
    /// <para>
    /// <c>props.pageProps</c> first, because Next puts a page's own data there; then the whole document, because not every
    /// page follows the convention and a value in the wrong place is still the value. The distinction is returned rather
    /// than hidden: <see cref="Found.PageProps"/> is the conventional path and <see cref="Found.Elsewhere"/> means the
    /// caller is relying on a search rather than on structure.
    /// </para>
    /// </summary>
    public static (JToken? Value, Found Where) FindProperty(string? dataJson, string propertyName)
    {
        if (string.IsNullOrEmpty(dataJson) || string.IsNullOrEmpty(propertyName))
            return (null, Found.Absent);

        JObject root;
        try
        {
            root = JObject.Parse(dataJson);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return (null, Found.Absent);
        }

        var inPageProps = root.SelectToken("props.pageProps." + propertyName);
        if (inPageProps != null && inPageProps.Type != JTokenType.Null)
            return (inPageProps, Found.PageProps);

        var anywhere = root.SelectToken("$.." + propertyName);
        if (anywhere != null && anywhere.Type != JTokenType.Null)
            return (anywhere, Found.Elsewhere);

        return (null, Found.Absent);
    }

    /// <summary>
    /// The page chunk paths in an HTML document, in the order they appear.
    ///
    /// <para>
    /// The build hash is per deployment, so the path cannot be constructed — it has to be read out of the page. Returns an
    /// empty list when the pattern is absent, which is what a non-Next page and a Next page served from a different
    /// router both look like.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> PageChunks(string? html)
    {
        if (string.IsNullOrEmpty(html)) return Array.Empty<string>();

        var found = new List<string>();
        foreach (Match m in Regex.Matches(html, PageChunkPattern))
            if (!found.Contains(m.Value))
                found.Add(m.Value);
        return found;
    }
}