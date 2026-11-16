namespace Cybersole.Stores.Scripts;

/// <summary>
/// The AddToCart family as a matrix rather than a list — thirteen names on at least three axes.
///
/// <para>
/// R939. Two rounds were spent discovering that two of five names were not frameworks, and the natural next question was
/// whether more names were misfiled. Scanning produced nine: the plain method, App, AppDw, Box, Dummy, GraphQL, Multi,
/// Preload and PreloadGraphQL. But that scan was truncated at forty matches and missed every framework-specific name,
/// which direct queries then confirmed exist — so the family is at least thirteen.
/// </para>
///
/// <code>
/// transport   plain (REST) · GraphQL
/// client      web · App · AppDw
/// purpose     plain · Preload · Multi · Dummy
/// parser      Next · Astro · Svelte · Frontend  (and Box, which is a shop step, not a parser)
/// </code>
///
/// <para>
/// The axes matter because they are independent: <c>AddToCartPreloadGraphQL</c> is transport times purpose, and
/// <c>AddToCartAppDw</c> is client times a platform. A list of thirteen hides that structure, and a list is also how two
/// names came to be misfiled in the first place. Counting what is implemented against a list of thirteen is a different
/// question from counting it against the product of these axes.
/// </para>
///
/// <para>
/// <b>What the image does not say.</b> Which combinations exist and which do not. Thirteen names are recovered, and the
/// axes explain them, but nothing says the grid is complete — <c>AddToCartAppGraphQL</c> is absent, whether because it is
/// unnecessary or because the scan has not reached it is unknown. So <see cref="Recovered"/> is the authority and the
/// axes are an explanation of it, never a way to generate a fourteenth name.
/// </para>
/// </summary>
public static class AddToCartMatrix
{
    /// <summary>
    /// Every name recovered so far, deduplicated after dropping the mangled-name suffix. Thirteen, and this is a lower
    /// bound: the scan truncated at forty matches and direct queries were needed to find four of them.
    /// </summary>
    internal static readonly string[] Recovered =
    {
        "AddToCart",
        "AddToCartApp",
        "AddToCartAppDw",
        "AddToCartBox",
        "AddToCartDummy",
        "AddToCartGraphQL",
        "AddToCartMulti",
        "AddToCartPreload",
        "AddToCartPreloadGraphQL",
        "AddToCartNext",
        "AddToCartAstro",
        "AddToCartSvelte",
        "AddToCartFrontend",
    };

    /// <summary>The three axes, with the values the recovered names show.</summary>
    internal static readonly (string Axis, string[] Values)[] Axes =
    {
        ("transport", new[] { "plain", "GraphQL" }),
        ("client", new[] { "web", "App", "AppDw" }),
        ("purpose", new[] { "plain", "Preload", "Multi", "Dummy" }),
        ("parser", new[] { "Next", "Astro", "Svelte", "Frontend" }),
    };

    /// <summary>Names that are neither a parser nor an axis value: Box is a shop step and belongs to PopMartDrawSteps.</summary>
    internal static readonly string[] NotParsers = { "AddToCartBox" };

    /// <summary>
    /// The axes a recovered name touches. Empty for a name the axes do not explain, which is the honest answer for one
    /// that was written down but never understood.
    /// </summary>
    public static IReadOnlyList<string> AxesOf(string? name)
    {
        if (string.IsNullOrEmpty(name)) return Array.Empty<string>();

        var hit = new List<string>();
        var rest = name!.StartsWith("AddToCart", StringComparison.Ordinal)
            ? name.Substring("AddToCart".Length)
            : name;

        foreach (var (axis, values) in Axes)
            foreach (var value in values)
                if (value != "plain" && rest.Contains(value, StringComparison.Ordinal))
                {
                    hit.Add(axis);
                    break;
                }

        return hit;
    }

    /// <summary>
    /// True when a name is explained by the axes alone. Box is the counter-example the image supplies, which is why the
    /// test exists rather than being assumed.
    /// </summary>
    public static bool IsExplainedByAxes(string? name) =>
        !string.IsNullOrEmpty(name) && AxesOf(name).Count > 0 && !NotParsers.Contains(name, StringComparer.Ordinal);

    /// <summary>
    /// How many of the recovered names are parsers, which is the subset a frontend surface would implement. Four, plus the
    /// umbrella the framework list already records.
    /// </summary>
    internal static readonly string[] ParserNames = { "AddToCartNext", "AddToCartAstro", "AddToCartSvelte", "AddToCartFrontend" };
}