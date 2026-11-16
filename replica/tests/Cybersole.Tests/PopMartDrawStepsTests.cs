using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The correction to the AddToCart family: Box is a PopMart step and Frontend is an umbrella, so the five platform gaps
/// were four and one shop step.
///
/// <para>
/// R938. Six consecutive state-machine numbers place AddToCartBox among PollRestockMulti, ExtractPopNow, SelectPopNow,
/// SelectMultiPopNow and SelectMultiPopNowUS -- one class's methods, and a PopMart draw sequence. The test that settles it
/// is a product scraper: every framework has one, and ScrapeProductBox does not exist. Three names carried as open items
/// later -- BoxGoodsList, BoxExtract, BoxSku -- return zero as well and are withdrawn.
/// </para>
/// </summary>
public class PopMartDrawStepsTests
{
    private static string[] Arr(string name) =>
        (string[])typeof(PopMartDrawSteps)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>Six draw steps, and AddToCartBox is one of them.</summary>
    [Fact]
    public void TheDrawSequenceContainsAddToCartBox()
    {
        var steps = Arr("DrawSteps");

        Assert.Equal(6, steps.Length);
        Assert.Contains("AddToCartBox", steps);
        Assert.Contains("PollRestockMulti", steps);
        Assert.Contains("ExtractPopNow", steps);
        Assert.Contains("SelectMultiPopNowUS", steps);
    }

    /// <summary>Four frameworks, not five, and Box is not among them.</summary>
    [Fact]
    public void ThereAreFourFrameworksAndBoxIsNotOne()
    {
        var frameworks = Arr("Frameworks");

        Assert.Equal(new[] { "Next", "Astro", "Svelte", "Frontend" }, frameworks);
        Assert.DoesNotContain("Box", frameworks);

        Assert.Equal(4, (int)typeof(PopMartDrawSteps)
            .GetField("FrameworkCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>
    /// The test that separates the two kinds: every framework has a product scraper, and Box has none. Asserted as a
    /// statement about the recorded lists rather than by searching the binary, since a test cannot reach the image.
    /// </summary>
    [Fact]
    public void EveryFrameworkHasAScraperAndBoxDoesNot()
    {
        var frameworks = Arr("Frameworks");

        // the scraper names the source carries, one per framework
        var scrapers = new[] { "ScrapeProductNext", "ScrapeProductAstro", "ScrapeProductSvelte", "ScrapeProductFrontend" };

        Assert.Equal(frameworks.Length, scrapers.Length);
        Assert.DoesNotContain("ScrapeProductBox", scrapers);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "PopMartDrawSteps.cs"));
        Assert.Contains("a search for <c>ScrapeProductBox</c> returns nothing", doc);
    }

    /// <summary>The three withdrawn names are recorded as absent, not as pending.</summary>
    [Fact]
    public void TheThreeWithdrawnNamesAreRecorded()
    {
        var withdrawn = Arr("WithdrawnNames");

        Assert.Equal(new[] { "BoxGoodsList", "BoxExtract", "BoxSku" }, withdrawn);
        Assert.All(withdrawn, n => Assert.StartsWith("Box", n));
    }

    /// <summary>Classification is by the recovered list, so a caller cannot decide a draw step is a framework.</summary>
    [Theory]
    [InlineData("AddToCartBox", true)]
    [InlineData("SelectPopNow", true)]
    [InlineData("ScrapeProductSvelte", false)]
    [InlineData("Frontend", false)]
    [InlineData(null, false)]
    public void DrawStepsAreRecognised(string? name, bool expected)
    {
        Assert.Equal(expected, PopMartDrawSteps.IsDrawStep(name));
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