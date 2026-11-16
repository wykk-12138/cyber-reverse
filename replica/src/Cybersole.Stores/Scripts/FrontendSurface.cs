namespace Cybersole.Stores.Scripts;

/// <summary>
/// The generic frontend path — and the reason "Frontend" never was a fourth framework.
///
/// <para>
/// R937. Box, Next, Astro and Svelte all turned out to be specific frontend parsers, so the fifth name looked like another
/// platform. It is not. The image's literals say what it is:
/// </para>
///
/// <code>
/// _frontendDomain · _frontendUrl · _frontendSearch · FrontendUri · get_FrontendUri · IsFrontendUrl
/// ScrapeJsonFrontend · ScrapePageFrontend · ScrapeProductFrontend
/// ScrapeVariantAvailabilityFrontend · FindProductFrontend · AddToCartFrontend
/// </code>
///
/// <para>
/// Every method in that list is a generic counterpart of a framework-specific one — <c>ScrapeProductFrontend</c> beside
/// <c>ScrapeProductSvelte</c>, <c>AddToCartFrontend</c> beside <c>AddToCartAstro</c>. And the fields are URI parts:
/// a domain, a url and a search, which is what <see cref="Uri"/> decomposes into. So the frontend path is the fallback
/// that reads whatever the site served, and the four frameworks are parsers it can call once it knows which one applies.
/// </para>
///
/// <para>
/// <b><c>IsFrontendUrl</c> is the hinge.</b> A store exposes an API and a page, and the two are different URLs on purpose —
/// so a flow has to decide which it is holding before it decides how to read it. That decision is what this class
/// exposes, and it is deliberately conservative: a URL that does not look like an API is treated as the frontend, because
/// reading a page as though it were JSON fails loudly while calling a page as though it were an API can return an HTML
/// error body that parses as nothing and looks like an empty product.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The API markers below. The image names <c>IsFrontendUrl</c> and nothing about what it tests,
/// so the markers are a list of what a storefront API looks like in practice rather than something recovered. They are
/// kept short and explicit so a wrong one is visible, and the method's default answer is chosen so that being wrong is
/// the loud kind of wrong.
/// </para>
/// </summary>
public static class FrontendSurface
{
    /// <summary>The three URI parts the image names as fields on a frontend descriptor.</summary>
    internal static readonly string[] UriParts = { "Domain", "Url", "Search" };

    /// <summary>
    /// Path segments that mark a URL as an API rather than a page. Inference: the image names the test and not its
    /// contents, so this is what a storefront API looks like rather than something recovered.
    /// </summary>
    internal static readonly string[] ApiPathMarkers =
    {
        "/api/", "/graphql", "/products.json", "/cart.js", "/cart/add.js", "/variants.json",
        "/scapi/", "/storefront/", "/__data.json", "/wp-json/",
    };

    /// <summary>The generic methods the image names, paired with the framework-specific ones they generalise.</summary>
    internal static readonly (string Generic, string? Specific)[] MethodFamily =
    {
        ("ScrapeJsonFrontend", null),
        ("ScrapePageFrontend", null),
        ("ScrapeProductFrontend", "ScrapeProductSvelte"),
        ("ScrapeVariantAvailabilityFrontend", "ScrapeVariantAvailabilityAstro"),
        ("FindProductFrontend", null),
        ("AddToCartFrontend", "AddToCartAstro"),
    };

    /// <summary>
    /// True when a URL looks like a storefront API rather than a page.
    ///
    /// <para>
    /// Query strings are ignored, since a page can carry any query and a marker in one would be a false positive. The
    /// comparison is case-insensitive because paths are not reliably cased across servers.
    /// </para>
    /// </summary>
    public static bool LooksLikeApi(string? url)
    {
        if (string.IsNullOrWhiteSpace(url)) return false;

        var path = url!;
        var q = path.IndexOf('?');
        if (q >= 0) path = path.Substring(0, q);

        foreach (var marker in ApiPathMarkers)
            if (path.IndexOf(marker, StringComparison.OrdinalIgnoreCase) >= 0)
                return true;
        return false;
    }

    /// <summary>
    /// True when a URL should be read as the frontend. The negation of <see cref="LooksLikeApi"/>, and stated separately
    /// because the default matters: anything not recognisably an API is a page, so a misclassification fails by reading
    /// HTML as JSON rather than by calling a page and parsing an error body as an empty product.
    /// </summary>
    public static bool IsFrontendUrl(string? url) => !LooksLikeApi(url);

    /// <summary>
    /// The URI parts of a frontend descriptor, split from a URL. The three the image names are the three this returns, so
    /// a caller building one cannot invent a fourth.
    /// </summary>
    public static IReadOnlyDictionary<string, string> Describe(string url)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["Domain"] = string.Empty,
            ["Url"] = string.Empty,
            ["Search"] = string.Empty,
        };

        if (string.IsNullOrWhiteSpace(url)) return result;

        if (!Uri.TryCreate(url, UriKind.Absolute, out var parsed))
        {
            // a relative path has no domain, and saying so is better than inventing one from context
            result["Url"] = url!;
            return result;
        }

        result["Domain"] = parsed.GetLeftPart(UriPartial.Authority);
        result["Url"] = parsed.AbsolutePath;
        result["Search"] = parsed.Query;
        return result;
    }
}