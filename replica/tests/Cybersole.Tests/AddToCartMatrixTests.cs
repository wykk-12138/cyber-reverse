using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The AddToCart family as thirteen names on four axes, and the scan that found only nine of them.
///
/// <para>
/// R939. Two rounds established that two of five names were misfiled, so the next question was whether more were. A scan
/// gave nine; direct queries showed it had missed every framework-specific name, so the family is at least thirteen. The
/// axes -- transport, client, purpose, parser -- explain the names, but the recovered list stays the authority, because
/// nothing says the grid is complete and a name generated from the axes would be an invention of exactly the kind these
/// rounds keep finding.
/// </para>
/// </summary>
public class AddToCartMatrixTests
{
    private static string[] Arr(string name) =>
        (string[])typeof(AddToCartMatrix)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>Thirteen recovered names, and this is a lower bound.</summary>
    [Fact]
    public void ThirteenNamesAreRecorded()
    {
        var names = Arr("Recovered");

        Assert.Equal(13, names.Length);
        Assert.Equal(13, names.Distinct().Count());
        Assert.All(names, n => Assert.StartsWith("AddToCart", n));
    }

    /// <summary>All four framework names survive into the list, which is what the truncated scan missed.</summary>
    [Fact]
    public void AllFourFrameworkNamesArePresent()
    {
        var names = Arr("Recovered");
        var parsers = Arr("ParserNames");

        Assert.Equal(4, parsers.Length);
        Assert.All(parsers, p => Assert.Contains(p, names));
        Assert.Equal(new[] { "AddToCartAstro", "AddToCartFrontend", "AddToCartNext", "AddToCartSvelte" },
                     parsers.OrderBy(p => p).ToArray());
    }

    /// <summary>The axes explain combinations rather than peers, which is the structure a flat list hides.</summary>
    [Theory]
    [InlineData("AddToCartPreloadGraphQL", new[] { "transport", "purpose" })]
    [InlineData("AddToCartAppDw", new[] { "client" })]
    [InlineData("AddToCartMulti", new[] { "purpose" })]
    [InlineData("AddToCartNext", new[] { "parser" })]
    public void AxesExplained(string name, string[] expected)
    {
        Assert.Equal(expected, AddToCartMatrix.AxesOf(name).ToArray());
    }

    /// <summary>
    /// Box is not explained by the axes, and that is the image's own counter-example: it is a shop step, so a name can be
    /// in the family without being a combination.
    /// </summary>
    [Fact]
    public void BoxIsNotExplainedByTheAxes()
    {
        Assert.False(AddToCartMatrix.IsExplainedByAxes("AddToCartBox"));
        Assert.Contains("AddToCartBox", Arr("NotParsers"));
        Assert.True(AddToCartMatrix.IsExplainedByAxes("AddToCartNext"));
    }

    /// <summary>
    /// The plain name touches no axis, which is correct: it is the base case, not a combination of values.
    /// </summary>
    [Fact]
    public void ThePlainNameTouchesNoAxis()
    {
        Assert.Empty(AddToCartMatrix.AxesOf("AddToCart"));
    }

    /// <summary>
    /// A generated fourteenth name would be an invention. Pinned by asserting the empty case answers empty rather than
    /// being filled in by the axes.
    /// </summary>
    [Theory]
    [InlineData("AddToCartAppGraphQL")]
    [InlineData("AddToCartZw")]
    public void ANameNotRecoveredIsNotExplained(string name)
    {
        // AppGraphQL combines two real axis values, so the axes would happily describe it -- and it is still not in the
        // recovered list. That is precisely why the list, not the axes, is the authority.
        Assert.DoesNotContain(name, Arr("Recovered"));
    }

    /// <summary>Four axes, with the values the names show.</summary>
    [Fact]
    public void TheAxesAreRecorded()
    {
        var axes = ((string, string[])[])typeof(AddToCartMatrix)
            .GetField("Axes", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(new[] { "transport", "client", "purpose", "parser" }, axes.Select(a => a.Item1).ToArray());
        Assert.Equal(new[] { "plain", "GraphQL" }, axes[0].Item2);
        Assert.Contains("AppDw", axes[1].Item2);
        Assert.Contains("Dummy", axes[2].Item2);
    }
}