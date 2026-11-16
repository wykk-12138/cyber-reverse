namespace Cybersole.Stores.Scripts;

/// <summary>
/// Where PopMart's box step sits, and why it was never a platform gap.
///
/// <para>
/// R938. The AddToCart work listed five platform gaps, Box first among them, and R937 found that Frontend was not a
/// platform at all. Box is not one either, for a different reason: the methods around it say what it belongs to.
/// </para>
///
/// <code>
/// &lt;PollRestockMulti&gt;d__81 · &lt;ExtractPopNow&gt;d__83 · &lt;SelectPopNow&gt;d__84
/// &lt;SelectMultiPopNow&gt;d__85 · &lt;AddToCartBox&gt;d__86 · &lt;SelectMultiPopNowUS&gt;d__87
/// </code>
///
/// <para>
/// Those six are consecutive state-machine numbers, which means they are six methods of one class, and the company they
/// keep is PopMart's: restock polling, extracting a pop-now, selecting one, selecting many, selecting many in the US,
/// then adding a box to the cart. So Box is a step in PopMart's draw flow, not a frontend framework -- and checking for a
/// product scraper settles it, because every framework has one: <c>ScrapeProductSvelte</c>, <c>ScrapeProductAstro</c> and
/// <c>ScrapeProductFrontend</c> all exist, while a search for <c>ScrapeProductBox</c> returns nothing.
/// </para>
///
/// <para>
/// <b>Why this is recorded rather than silently fixed.</b> The list of five was wrong in two directions at once: one
/// member was an umbrella and another was a shop-specific step. Both mistakes came from reading a flat list of names and
/// assuming the names were peers, and both were only detectable by asking what surrounds each name. Keeping the
/// correction in code means the next person reading the AddToCart family sees why two of the five are not there.
/// </para>
///
/// <para>
/// <b>Also settled.</b> Three names had been carried in the backlog as "no callers, deliberately not forced" — BoxGoodsList,
/// BoxExtract and BoxSku. Searches return zero for all three, so they were never in the image; they were invented during
/// an earlier reading of the box code and have now been withdrawn.
/// </para>
/// </summary>
public static class PopMartDrawSteps
{
    /// <summary>
    /// The six consecutive state machines the image carries, in ordinal order. Consecutive because they are methods of
    /// one class, which is what makes them a sequence rather than a coincidence.
    /// </summary>
    internal static readonly string[] DrawSteps =
    {
        "PollRestockMulti", "ExtractPopNow", "SelectPopNow",
        "SelectMultiPopNow", "AddToCartBox", "SelectMultiPopNowUS",
    };

    /// <summary>The three names that were carried as open items and are absent from the image.</summary>
    internal static readonly string[] WithdrawnNames = { "BoxGoodsList", "BoxExtract", "BoxSku" };

    /// <summary>
    /// The frontend frameworks, which is four and not five. Each has a product scraper, which is the test Box fails.
    /// </summary>
    internal static readonly string[] Frameworks = { "Next", "Astro", "Svelte", "Frontend" };

    /// <summary>
    /// True when a name is a draw step rather than a framework. Checked against the recovered list so a caller cannot
    /// decide for itself.
    /// </summary>
    public static bool IsDrawStep(string? name) =>
        !string.IsNullOrEmpty(name) && DrawSteps.Contains(name, StringComparer.Ordinal);

    /// <summary>
    /// The count of frontend frameworks, four, stated separately from the array so a reader comparing it with the old
    /// "five platform gaps" figure sees the correction rather than an unexplained change.
    /// </summary>
    internal const int FrameworkCount = 4;
}