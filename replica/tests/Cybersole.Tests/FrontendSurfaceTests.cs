using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The generic frontend path, and the finding that "Frontend" was never a fourth framework.
///
/// <para>
/// R937. Box, Next, Astro and Svelte were all specific parsers, so the fifth name read like another platform. The
/// literals say otherwise: ScrapeProductFrontend sits beside ScrapeProductSvelte, AddToCartFrontend beside
/// AddToCartAstro, and the fields are URI parts. So this is the fallback that reads whatever the site served, and the four
/// frameworks are parsers it calls once it knows which applies. IsFrontendUrl is the hinge, and its default is chosen so
/// that a mistake fails loudly.
/// </para>
/// </summary>
public class FrontendSurfaceTests
{
    private static string[] Const(string name) =>
        (string[])typeof(FrontendSurface)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>The three URI parts the image names as fields, and no fourth.</summary>
    [Fact]
    public void TheThreeUriPartsAreTheRecoveredOnes()
    {
        Assert.Equal(new[] { "Domain", "Url", "Search" }, Const("UriParts"));

        var described = FrontendSurface.Describe("https://shop.example.com/p/air?size=9");
        Assert.Equal(3, described.Count);
        Assert.Equal(new[] { "Domain", "Search", "Url" }, described.Keys.OrderBy(k => k).ToArray());
    }

    /// <summary>Each generic method generalises a framework-specific one, or stands alone where there is no counterpart.</summary>
    [Fact]
    public void TheMethodFamilyPairsGenericWithSpecific()
    {
        var pairs = (ValueTuple<string, string?>[])typeof(FrontendSurface)
            .GetField("MethodFamily", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(6, pairs.Length);
        Assert.All(pairs, p => Assert.EndsWith("Frontend", p.Item1));

        var withCounterpart = pairs.Where(p => p.Item2 != null).ToArray();
        Assert.Equal(3, withCounterpart.Length);
        Assert.Contains(withCounterpart, p => p.Item2 == "ScrapeProductSvelte");
        Assert.Contains(withCounterpart, p => p.Item2 == "AddToCartAstro");
    }

    /// <summary>API markers are recognised, and the query string is ignored so a page cannot be mistaken for one.</summary>
    [Theory]
    [InlineData("/api/cart/add", true)]
    [InlineData("/graphql", true)]
    [InlineData("/products.json", true)]
    [InlineData("/cart.js", true)]
    [InlineData("/__data.json", true)]
    [InlineData("/products/air-max", false)]
    [InlineData("/p/123?next=/api/x", false)]
    public void ApiMarkersAreRecognisedAndQueriesIgnored(string url, bool expected)
    {
        Assert.Equal(expected, FrontendSurface.LooksLikeApi(url));
        Assert.Equal(!expected, FrontendSurface.IsFrontendUrl(url));
    }

    /// <summary>
    /// The default is the loud kind of wrong: an unrecognised URL is a page, so a mistake reads HTML as JSON and fails,
    /// rather than calling a page as an API and parsing an error body as an empty product.
    /// </summary>
    [Fact]
    public void AnUnrecognisableUrlIsTreatedAsAPage()
    {
        Assert.True(FrontendSurface.IsFrontendUrl("/something/made/up"));
        Assert.True(FrontendSurface.IsFrontendUrl(""));
        Assert.True(FrontendSurface.IsFrontendUrl(null));

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "FrontendSurface.cs"));
        Assert.Contains("fails loudly", doc);
    }

    /// <summary>Describing splits authority, path and query, and leaves the search out of the path.</summary>
    [Fact]
    public void DescribingSplitsTheThreeParts()
    {
        var d = FrontendSurface.Describe("https://shop.example.com:8443/p/air?size=9&colour=red");

        Assert.Equal("https://shop.example.com:8443", d["Domain"]);
        Assert.Equal("/p/air", d["Url"]);
        Assert.Equal("?size=9&colour=red", d["Search"]);
    }

    /// <summary>A relative path has no domain, and the description says so rather than inventing one.</summary>
    [Fact]
    public void ARelativePathHasNoDomain()
    {
        var d = FrontendSurface.Describe("/p/air?x=1");

        Assert.Equal("", d["Domain"]);
        Assert.Equal("/p/air?x=1", d["Url"]);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}