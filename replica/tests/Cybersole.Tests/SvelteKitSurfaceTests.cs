using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// SvelteKit pages, whose mechanism is the most completely recovered of the three platforms.
///
/// <para>
/// R936. Five literals describe the calls rather than just the framework: the data endpoint with its invalidated query,
/// the nonce cookie prefix, two route headers, and a type name. A SvelteKit page's data sits at the route's own path plus
/// /__data.json, the route and its query travel in headers rather than in the URL, and the invalidated counter says which
/// generation of data the client holds. These tests pin the endpoint shape and, most of all, that both headers are always
/// sent -- one without the other describes a route whose query the server cannot see.
/// </para>
/// </summary>
public class SvelteKitSurfaceTests
{
    private static string Const(string name) =>
        (string)typeof(SvelteKitSurface)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    /// <summary>The five literals, verbatim.</summary>
    [Fact]
    public void TheFiveLiteralsAreTheRecoveredOnes()
    {
        Assert.Equal("/__data.json", Const("DataPath"));
        Assert.Equal("/__data.json?x-sveltekit-invalidated=001", Const("DataEndpoint"));
        Assert.Equal("__sveltekit", Const("NonceCookiePrefix"));
        Assert.Equal("x-sveltekit-pathname", Const("PathnameHeader"));
        Assert.Equal("x-sveltekit-search", Const("SearchHeader"));

        Assert.Equal(5, (int)typeof(SvelteKitSurface)
            .GetField("RecoveredLiteralCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>The endpoint literal is what DataUrl produces when asked for the root with the default counter.</summary>
    [Fact]
    public void TheRootRouteReproducesTheRecoveredEndpoint()
    {
        Assert.Equal(Const("DataEndpoint"), SvelteKitSurface.DataUrl("/"));
        Assert.Equal(Const("DataEndpoint"), SvelteKitSurface.DataUrl(""));
    }

    /// <summary>A route's own path precedes the endpoint, and a trailing slash does not double up.</summary>
    [Theory]
    [InlineData("/products/air-max", "/products/air-max/__data.json?x-sveltekit-invalidated=001")]
    [InlineData("/products/air-max/", "/products/air-max/__data.json?x-sveltekit-invalidated=001")]
    public void ARoutePrefixesTheEndpoint(string route, string expected)
    {
        Assert.Equal(expected, SvelteKitSurface.DataUrl(route));
    }

    /// <summary>The counter is a parameter rather than a constant, since nothing says how it advances.</summary>
    [Fact]
    public void TheInvalidatedCounterCanBeSet()
    {
        Assert.EndsWith("x-sveltekit-invalidated=002", SvelteKitSurface.DataUrl("/x", "002"));
    }

    /// <summary>
    /// Both headers are always present. One alone describes a route whose query the server cannot see, which is the case
    /// the headers exist to prevent.
    /// </summary>
    [Fact]
    public void BothHeadersAreAlwaysSent()
    {
        var withQuery = SvelteKitSurface.DataHeaders("/p", "a=1");
        Assert.Equal("/p", withQuery["x-sveltekit-pathname"]);
        Assert.Equal("?a=1", withQuery["x-sveltekit-search"]);

        var without = SvelteKitSurface.DataHeaders("/p");
        Assert.Equal("/p", without["x-sveltekit-pathname"]);
        Assert.Equal("", without["x-sveltekit-search"]);

        var rooted = SvelteKitSurface.DataHeaders("");
        Assert.Equal("/", rooted["x-sveltekit-pathname"]);
    }

    /// <summary>The nonce family is matched by prefix, including the __Host- form.</summary>
    [Theory]
    [InlineData("__sveltekit-abc", true)]
    [InlineData("__Host-__sveltekit-x", true)]
    [InlineData("__sveltekitz", false)]
    [InlineData("sveltekit", false)]
    [InlineData("", false)]
    [InlineData(null, false)]
    public void TheNonceFamilyIsMatchedByPrefix(string? name, bool expected)
    {
        Assert.Equal(expected, SvelteKitSurface.IsNonceCookie(name));
    }

    /// <summary>The detection is weak by construction, and says so.</summary>
    [Fact]
    public void DetectionIsWeakAndSaysSo()
    {
        Assert.True(SvelteKitSurface.LooksLikeSvelteKit("<a href=\"/x/__data.json\">d</a>"));
        Assert.True(SvelteKitSurface.LooksLikeSvelteKit("<script>__sveltekit</script>"));
        Assert.False(SvelteKitSurface.LooksLikeSvelteKit("<html></html>"));
        Assert.False(SvelteKitSurface.LooksLikeSvelteKit(null));

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "SvelteKitSurface.cs"));
        Assert.Contains("Weak in the", doc);
    }

    /// <summary>The method family names three platform steps plus the two that serve every platform.</summary>
    [Fact]
    public void TheMethodFamilyIsRecorded()
    {
        var family = (string[])typeof(SvelteKitSurface)
            .GetField("MethodFamily", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(new[] { "ScrapeProductSvelte", "CheckPriceLimitSvelte", "AddToCartSvelte", "RefreshSession", "DetectStorefront" }, family);
        Assert.Equal(3, family.Count(n => n.EndsWith("Svelte")));
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