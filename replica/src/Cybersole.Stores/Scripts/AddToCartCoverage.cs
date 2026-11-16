namespace Cybersole.Stores.Scripts;

/// <summary>
/// How much of each AddToCart name the replica actually has, in three columns rather than one.
///
/// <para>
/// R940. Asked how many of the thirteen the replica held, a name search answered thirteen of thirteen -- and six of those
/// were only occurrences in the list written the round before. That is R850's shape without content: a name in a table is
/// not a method. Splitting the count gives eight implemented and five named only.
/// </para>
///
/// <para>
/// The five are not all the same kind of gap, though, and one distinction matters more than the rest. Four of them --
/// Next, Astro, Svelte and Frontend -- each have a <b>surface</b>: a class that knows how to read that page's data. What
/// they lack is a <b>step</b>: the call that turns a read product into a cart line. So for those four the question is not
/// "is anything there" but "where does this framework's cart accept a POST", and that is a different question with a
/// different answer, which the image does not supply.
/// </para>
///
/// <para>
/// <b>Why the surfaces do not imply the steps.</b> A surface answers how to read; a step answers where to write. Reading a
/// Next page means parsing <c>script#__NEXT_DATA__</c>, and writing to its cart means calling the store's cart endpoint,
/// which differs per shop rather than per framework -- two shops on the same framework have different cart URLs. So the
/// four surfaces cannot be composed into four steps, and claiming otherwise would be inventing endpoint addresses.
/// </para>
///
/// <para>
/// <b>AddToCartDummy</b> is the fifth and a different case again: its name says it does not talk to a shop at all, which
/// makes it the one of the five that need not wait on endpoint evidence.
/// </para>
/// </summary>
public static class AddToCartCoverage
{
    /// <summary>
    /// Per name: whether the replica has an implementation, whether it has only a mention, and what a surface does or does
    /// not give it.
    /// </summary>
    internal static readonly (string Name, bool Implemented, string Note)[] Rows =
    {
        ("AddToCart", true, "generic step, used by the Demandware paths"),
        ("AddToCartApp", true, "app client path"),
        ("AddToCartAppDw", true, "app client on Demandware"),
        ("AddToCartBox", true, "PopMart draw step"),
        // R941: the note said a dry run, which was wrong. AddToCartDummy is followed immediately by RemoveDummy, so it is
        // a placeholder item added early and removed later -- cart priming. The name is about the item, not the call.
        ("AddToCartDummy", false, "named only: cart priming with RemoveDummy, not a dry run"),
        ("AddToCartGraphQL", true, "GraphQL transport"),
        // R942: adjacency puts this in PopMart's class beside AddToCartDummy and RemoveDummy, so it is add-many-boxes
        // rather than a generic multi-item cart. The fourth misfiling in four rounds.
        ("AddToCartMulti", true, "PopMart add-many-boxes, not a generic multi-item cart"),
        ("AddToCartPreload", true, "cart preload"),
        ("AddToCartPreloadGraphQL", true, "preload over GraphQL"),
        ("AddToCartNext", false, "surface exists, step does not: the cart endpoint is per shop, not per framework"),
        ("AddToCartAstro", false, "surface exists, step does not: same reason"),
        ("AddToCartSvelte", false, "surface exists, step does not: same reason"),
        ("AddToCartFrontend", false, "surface exists, step does not: same reason"),
    };

    /// <summary>
    /// The four whose surface is in place and whose step is not, which is the shape most likely to be misread as done.
    /// </summary>
    internal static readonly string[] SurfaceWithoutStep =
    {
        "AddToCartNext", "AddToCartAstro", "AddToCartSvelte", "AddToCartFrontend",
    };

    /// <summary>
    /// The name whose absence was thought not to depend on endpoint evidence, which R941 corrected: it is cart
    /// priming, so what it needs is a placeholder item rather than a recovered cart address -- a per-shop datum.
    /// </summary>
    internal const string IndependentGap = "AddToCartDummy";

    /// <summary>The counts, stated rather than derived, so a reader comparing them with an earlier figure sees the split.</summary>
    internal const int ImplementedCount = 8;
    internal const int NamedOnlyCount = 5;

    /// <summary>True when the replica implements the named method rather than merely mentioning it.</summary>
    public static bool IsImplemented(string? name)
    {
        if (string.IsNullOrEmpty(name)) return false;
        foreach (var row in Rows)
            if (string.Equals(row.Name, name, StringComparison.Ordinal))
                return row.Implemented;
        return false;
    }

    /// <summary>
    /// True when a surface exists for the name but no step does. This is the distinction a single count hides, and the one
    /// that would let a reader conclude four more are finished than are.
    /// </summary>
    public static bool HasSurfaceWithoutStep(string? name) =>
        !string.IsNullOrEmpty(name) && SurfaceWithoutStep.Contains(name, StringComparer.Ordinal);
}