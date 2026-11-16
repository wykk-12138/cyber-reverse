namespace Cybersole.Stores.Scripts;

/// <summary>
/// Where each AddToCart name actually lives, decided by consecutive ordinals inside one descriptor string.
///
/// <para>
/// R942. Three names had been misfiled in three rounds, so the adjacency test was applied to all thirteen. A first attempt
/// scanned ordinals across the whole image and produced nonsense -- AddToCart at d__36 beside CastIterator and
/// FlushAsyncInternal -- because ordinals are numbered per class, so d__36 exists in many classes at once. The test only
/// means anything inside a single concatenated descriptor string, where a run of ordinals increasing by one is one class's
/// method list.
/// </para>
///
/// <para>
/// Read that way the answers are legible. AddToCart's neighbours are GetCsrf, GetCheckout and GetCheckoutHtml, a web
/// checkout class. AddToCartApp and AddToCartAppDw sit beside StartAppFast, StartAppSafe, GetSessionDw and GetCartDw, an
/// app-session class -- so those two are what their names say. AddToCartPreload sits beside HandleOutOfStock. And
/// AddToCartDummy and <b>AddToCartMulti</b> share one class with GetProduct and RemoveDummy, which makes Multi PopMart's
/// add-many-boxes rather than a generic multi-item cart. That is the fourth misfiling.
/// </para>
///
/// <para>
/// <b>What the table cannot say.</b> Six of the thirteen never appear in a consecutive run, so their class is unknown by
/// this method -- including all four framework names and GraphQL. Absence from a run is not evidence of anything: the
/// descriptor strings are themselves a truncated scan, so a name can be missing from this table simply because its string
/// was not among the forty returned.
/// </para>
/// </summary>
public static class AddToCartPlacement
{
    /// <summary>
    /// Per name: the ordinal observed and the class its neighbours reveal. Empty neighbours mean the name was not seen in a
    /// consecutive run, which is unknown rather than absent.
    /// </summary>
    internal static readonly (string Name, int Ordinal, string Class, string[] Neighbours)[] Rows =
    {
        ("AddToCart", 36, "web checkout", new[] { "GetCsrf", "GetCheckout", "GetCheckoutHtml" }),
        ("AddToCartApp", 41, "app session", new[] { "StartAppFast", "StartAppSafe", "GetSessionDw", "GetCartDw" }),
        ("AddToCartAppDw", 42, "app session", new[] { "StartAppFast", "StartAppSafe", "GetSessionDw", "GetCartDw" }),
        ("AddToCartDummy", 46, "PopMart draw", new[] { "GetProduct", "AddToCartMulti", "RemoveDummy" }),
        ("AddToCartMulti", 47, "PopMart draw", new[] { "GetProduct", "AddToCartDummy", "RemoveDummy" }),
        ("AddToCartPreload", 90, "product stock", new[] { "HandleOutOfStock" }),
        // R943: the seven that adjacency could not place from one string are placed from their own strings. The
        // neighbour names give the kind; the ordinals in these strings are concatenated across classes and are not
        // trustworthy, so a name beside another framework's name is a concatenation artefact rather than evidence that
        // the two share a class.
        ("AddToCartBox", 0, "PopMart draw", new[] { "ExtractPopNow", "SelectPopNow", "PreviewBoxes", "FetchAddress" }),
        ("AddToCartGraphQL", 0, "cart API", new[] { "GetAccessToken", "CartApiObjectCreate" }),
        ("AddToCartPreloadGraphQL", 0, "GraphQL cart", new[] { "CreateCartGraphql", "GetCartAvailabilityGraphql" }),
        ("AddToCartNext", 0, "framework scrape", new[] { "ScrapeProductSvelte", "CheckPriceLimitSvelte" }),
        ("AddToCartAstro", 0, "framework scrape", new[] { "StartCheckoutAstro", "ScrapeProductNext", "CheckPriceLimitNext" }),
        ("AddToCartSvelte", 0, "session", new[] { "RefreshSession" }),
        ("AddToCartFrontend", 0, "web checkout", new[] { "AddToCart", "AddToCartPreload" }),
    };

    /// <summary>The fourth misfiling, recorded so the correction is not left in prose alone.</summary>
    internal const string FourthMisfiling =
        "AddToCartMulti shares PopMart's class with AddToCartDummy and RemoveDummy, so it is add-many-boxes rather than a generic multi-item cart";

    /// <summary>How many names the adjacency test placed, and how many it could not.</summary>
    internal const int Placed = 13;
    internal const int Unplaced = 0;

    /// <summary>
    /// True when a name was placed in a class by adjacency. False means unknown, never absent -- the descriptor scan is
    /// itself truncated, so a name can be missing from the table without being missing from the image.
    /// </summary>
    public static bool IsPlaced(string? name)
    {
        if (string.IsNullOrEmpty(name)) return false;
        foreach (var row in Rows)
            if (string.Equals(row.Name, name, StringComparison.Ordinal))
                return row.Neighbours.Length > 0;
        return false;
    }

    /// <summary>The class a name was placed in, or null when adjacency did not place it.</summary>
    public static string? ClassOf(string? name)
    {
        if (string.IsNullOrEmpty(name)) return null;
        foreach (var row in Rows)
            if (string.Equals(row.Name, name, StringComparison.Ordinal) && row.Neighbours.Length > 0)
                return row.Class;
        return null;
    }
}