using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Next.js pages, from the four literals the image carries.
///
/// <para>
/// R934. Unlike Astro and Svelte, which the image names only as words, Next comes with a selector and a path pattern:
/// <c>script#__NEXT_DATA__</c> and <c>/_next/static/chunks/app/[^"']*?page-[0-9a-f]+\.js</c>. Those two say the mechanism
/// outright, so this class can be checked against them. The property lookup is where inference enters, and it reports
/// which path it used because "found by convention" and "found by search" are different claims.
/// </para>
/// </summary>
public class NextJsSurfaceTests
{
    private static string Const(string name) =>
        (string)typeof(NextJsSurface)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    /// <summary>The four literals, verbatim — a selector, a regex, and two asset roots.</summary>
    [Fact]
    public void TheFourLiteralsAreTheRecoveredOnes()
    {
        Assert.Equal("script#__NEXT_DATA__", Const("DataSelector"));
        Assert.Equal(@"/_next/static/chunks/app/[^""']*?page-[0-9a-f]+\.js", Const("PageChunkPattern"));
        Assert.Equal("/_next/", Const("AssetRoot"));
        Assert.Equal("/pay/_next/", Const("PayAssetRoot"));

        Assert.Equal(4, (int)typeof(NextJsSurface)
            .GetField("RecoveredLiteralCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>The data is found by id, not by being the first script on the page.</summary>
    [Fact]
    public void TheDataIsFoundByItsIdWhateverTheScriptOrder()
    {
        var html = "<html><script>var a=1;</script>" +
                   "<script id=\"__NEXT_DATA__\" type=\"application/json\">{\"props\":{\"pageProps\":{\"sku\":\"A1\"}}}</script>" +
                   "<script>var b=2;</script></html>";

        var json = NextJsSurface.ExtractDataJson(html);

        Assert.NotNull(json);
        Assert.Contains("\"sku\":\"A1\"", json);
    }

    /// <summary>Single-quoted and unquoted id forms are both accepted, since the attribute's quoting is the page's business.</summary>
    [Theory]
    [InlineData("<script id='__NEXT_DATA__'>{}</script>")]
    [InlineData("<script id=__NEXT_DATA__>{}</script>")]
    [InlineData("<script type=\"application/json\" id=\"__NEXT_DATA__\">{}</script>")]
    public void TheAttributeQuotingDoesNotMatter(string html)
    {
        Assert.Equal("{}", NextJsSurface.ExtractDataJson(html));
    }

    /// <summary>No tag, or an empty one, both give null — "not a Next page" and "a Next page with no data" look alike.</summary>
    [Theory]
    [InlineData("<html><body>plain</body></html>")]
    [InlineData("<script id=\"__NEXT_DATA__\"></script>")]
    [InlineData("")]
    [InlineData(null)]
    public void MissingOrEmptyDataIsNull(string? html)
    {
        Assert.Null(NextJsSurface.ExtractDataJson(html));
    }

    /// <summary>
    /// The conventional path is reported as such, and a value elsewhere is reported as elsewhere. Collapsing the two
    /// would tell a caller its structure was confirmed when only a search had succeeded.
    /// </summary>
    [Fact]
    public void WhereTheValueWasFoundIsReported()
    {
        var conventional = "{\"props\":{\"pageProps\":{\"sku\":\"A1\"}}}";
        var (v1, w1) = NextJsSurface.FindProperty(conventional, "sku");
        Assert.Equal(NextJsSurface.Found.PageProps, w1);
        Assert.Equal("A1", v1!.ToString());

        var unusual = "{\"props\":{\"other\":{\"sku\":\"B2\"}}}";
        var (v2, w2) = NextJsSurface.FindProperty(unusual, "sku");
        Assert.Equal(NextJsSurface.Found.Elsewhere, w2);
        Assert.Equal("B2", v2!.ToString());

        var (v3, w3) = NextJsSurface.FindProperty(conventional, "nope");
        Assert.Equal(NextJsSurface.Found.Absent, w3);
        Assert.Null(v3);
    }

    /// <summary>Malformed JSON is absent rather than an exception, since a page can embed anything.</summary>
    [Fact]
    public void MalformedJsonIsAbsentNotAThrow()
    {
        var (value, where) = NextJsSurface.FindProperty("{not json", "sku");
        Assert.Equal(NextJsSurface.Found.Absent, where);
        Assert.Null(value);
    }

    /// <summary>
    /// The page chunk is read out of the document, because the build hash is per deployment and cannot be constructed.
    /// Duplicates collapse, since the same chunk is usually referenced more than once.
    /// </summary>
    [Fact]
    public void PageChunksAreReadOutAndDeduplicated()
    {
        var html = "<script src=\"/_next/static/chunks/app/products/page-1a2b3c.js\"></script>" +
                   "<script src=\"/_next/static/chunks/app/products/page-1a2b3c.js\"></script>" +
                   "<script src=\"/_next/static/chunks/app/other/page-9f8e7d.js\"></script>";

        var chunks = NextJsSurface.PageChunks(html);

        Assert.Equal(2, chunks.Count);
        Assert.Contains("/_next/static/chunks/app/products/page-1a2b3c.js", chunks);
        Assert.DoesNotContain("/_next/static/chunks/app/other/page-9f8e7d.js", chunks.Where(c => c.EndsWith("1a2b3c.js")));
    }

    /// <summary>A page with no matching chunk gives an empty list, which is also what a non-Next page gives.</summary>
    [Fact]
    public void NoChunksIsAnEmptyList()
    {
        Assert.Empty(NextJsSurface.PageChunks("<html></html>"));
        Assert.Empty(NextJsSurface.PageChunks(null));
    }

    /// <summary>
    /// The chunk pattern must not match the legacy pages-router form, which is /_next/static/chunks/pages/... — the
    /// literal names `chunks/app/`, and treating the two routers as one would build a path the image does not use.
    /// </summary>
    [Fact]
    public void TheLegacyPagesRouterDoesNotMatch()
    {
        var html = "<script src=\"/_next/static/chunks/pages/index-abc123.js\"></script>";
        Assert.Empty(NextJsSurface.PageChunks(html));
    }
}