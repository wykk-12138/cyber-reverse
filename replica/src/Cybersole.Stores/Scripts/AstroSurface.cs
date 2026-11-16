using System.Text.RegularExpressions;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Astro product pages — a framework whose whole handle in the image is one attribute prefix and a family of methods.
///
/// <para>
/// R935. Astro looked like the weakest of the four AddToCart gaps: the image names only the framework. But it names a
/// great deal more than that on inspection -- <c>ScrapeProductAstro</c>, <c>ScrapeVariantAvailabilityAstro</c>,
/// <c>CheckPriceLimitAstro</c>, <c>AddToCartAstro</c>, <c>StartCheckoutAstro</c>, <c>ParseAstroProduct</c>,
/// <c>ParseAstroImage</c>, and the three names <c>AstroAttribute</c>, <c>AstroProp</c>, <c>AstroProps</c>. So Astro is a
/// parallel code path, not a branch inside the generic one.
/// </para>
///
/// <para>
/// <b>The marker.</b> One literal explains the mechanism: <c>data-astro-cid</c>. Astro stamps every element it renders
/// with <c>data-astro-cid-XXXX</c>, a per-build suffix used to scope its styles -- which is why the method family carries
/// an <c>Attribute</c> name beside its <c>Prop</c> names. Nothing in the image says <c>astro-island</c>,
/// <c>component-url</c> or a <c>props=</c> attribute, so the island mechanism is not what the original reads. Searching
/// for those first was worth doing for exactly that reason: it ruled out the obvious guess.
/// </para>
///
/// <para>
/// <b>Why the suffix cannot be hard-coded.</b> Like Next's build hash, the cid suffix changes with the build, so the
/// attribute has to be matched by prefix. <see cref="AttributePattern"/> matches the family and
/// <see cref="Attributes"/> lists what a page actually carries, which is the useful thing for a caller deciding which
/// element is the product's.
/// </para>
///
/// <para>
/// <b>What is inference.</b> That the attribute is how a product is located. The image gives the prefix and the method
/// names, and the two fit together, but no recovered code shows a selector built from them. So this class exposes the
/// matching and the listing and does not claim to know which element holds the product; that decision is left where the
/// evidence is thin.
/// </para>
/// </summary>
public static class AstroSurface
{
    /// <summary>The prefix the image carries, verbatim.</summary>
    internal const string CidPrefix = "data-astro-cid";

    /// <summary>
    /// The full attribute family: the prefix followed by a build-specific suffix. Anchored on the hyphen so a hypothetical
    /// <c>data-astro-cidx</c> would not match, and case-insensitive because HTML attribute names are.
    /// </summary>
    internal const string AttributePattern = @"\bdata-astro-cid-[A-Za-z0-9_-]+";

    /// <summary>The methods the image names, in the order they appear in a task's life.</summary>
    internal static readonly string[] MethodFamily =
    {
        "ScrapeProductAstro", "ScrapeVariantAvailabilityAstro", "CheckPriceLimitAstro",
        "AddToCartAstro", "StartCheckoutAstro", "ParseAstroProduct", "ParseAstroImage",
    };

    /// <summary>
    /// Every distinct cid attribute in a document, in the order first seen.
    ///
    /// <para>
    /// A page carries one per component that renders elements, so the list is how many scopes it has -- usually one for
    /// the page shell and one for the component holding the buy controls. Which is which is not recoverable from the
    /// attribute alone, and this returns the list rather than guessing an order.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> Attributes(string? html)
    {
        if (string.IsNullOrEmpty(html)) return Array.Empty<string>();

        var found = new List<string>();
        foreach (Match m in Regex.Matches(html, AttributePattern, RegexOptions.IgnoreCase))
        {
            var name = m.Value;
            if (!found.Any(f => string.Equals(f, name, StringComparison.OrdinalIgnoreCase)))
                found.Add(name);
        }
        return found;
    }

    /// <summary>
    /// True when a document carries any cid attribute, which is the cheapest test for "this page was rendered by Astro".
    ///
    /// <para>
    /// A false answer is not proof of the opposite: a page can be Astro-rendered with every scoped style stripped. It is
    /// used to decide whether the Astro path is worth trying, not to conclude that a page is not Astro.
    /// </para>
    /// </summary>
    public static bool LooksLikeAstro(string? html) => Attributes(html).Count > 0;

    /// <summary>
    /// The span of a document that carries a given cid attribute, from the first element bearing it to the end of that
    /// element's tag. Enough to identify which element a scope belongs to without pretending to parse the tree.
    /// </summary>
    public static IReadOnlyList<string> TagsWith(string? html, string cidAttribute)
    {
        if (string.IsNullOrEmpty(html) || string.IsNullOrEmpty(cidAttribute))
            return Array.Empty<string>();

        var found = new List<string>();
        foreach (Match m in Regex.Matches(html, @"<[a-zA-Z][^>]*\b" + Regex.Escape(cidAttribute) + @"\b[^>]*>",
                     RegexOptions.IgnoreCase))
            found.Add(m.Value);
        return found;
    }
}