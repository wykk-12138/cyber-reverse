using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The three-column count: implemented, named only, and surface-without-step.
///
/// <para>
/// R940. A name search said thirteen of thirteen, and six of those were mentions in the list written a round earlier --
/// R850's shape without content. The split is eight implemented and five named only, and of the five four have a surface
/// and no step. That last distinction is the one a single count hides: a reader would take four surfaces as four
/// finished steps.
/// </para>
/// </summary>
public class AddToCartCoverageTests
{
    private static (string Name, bool Implemented, string Note)[] Rows() =>
        ((string, bool, string)[])typeof(AddToCartCoverage)
            .GetField("Rows", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    private static string[] Arr(string name) =>
        (string[])typeof(AddToCartCoverage)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>Thirteen rows, split eight and five, and the counts are stated rather than derived.</summary>
    [Fact]
    public void TheSplitIsEightImplementedAndFiveNamedOnly()
    {
        var rows = Rows();

        Assert.Equal(13, rows.Length);
        Assert.Equal(8, rows.Count(r => r.Implemented));
        Assert.Equal(5, rows.Count(r => !r.Implemented));

        Assert.Equal(8, (int)typeof(AddToCartCoverage)
            .GetField("ImplementedCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
        Assert.Equal(5, (int)typeof(AddToCartCoverage)
            .GetField("NamedOnlyCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>Every row carries a note, so no gap is left unexplained.</summary>
    [Fact]
    public void EveryRowExplainsItself()
    {
        Assert.All(Rows(), r => Assert.False(string.IsNullOrWhiteSpace(r.Note)));
    }

    /// <summary>The four framework names each have a surface and no step, and that is stated as such.</summary>
    [Fact]
    public void FourHaveASurfaceWithoutAStep()
    {
        var surfaces = Arr("SurfaceWithoutStep");

        Assert.Equal(new[] { "AddToCartNext", "AddToCartAstro", "AddToCartSvelte", "AddToCartFrontend" }, surfaces);
        Assert.All(surfaces, s => Assert.False(AddToCartCoverage.IsImplemented(s)));
        Assert.All(surfaces, s => Assert.True(AddToCartCoverage.HasSurfaceWithoutStep(s)));
    }

    /// <summary>
    /// The reason a surface cannot become a step: the cart endpoint varies per shop rather than per framework, so
    /// composing the four surfaces would mean inventing addresses.
    /// </summary>
    [Fact]
    public void TheSurfaceDoesNotImplyTheStep()
    {
        var rows = Rows().Where(r => r.Name == "AddToCartNext").ToArray();
        Assert.Single(rows);
        Assert.Contains("per shop", rows[0].Note);

        Assert.All(Arr("SurfaceWithoutStep"), s =>
        {
            var row = Rows().Single(r => r.Name == s);
            Assert.Contains("step does not", row.Note);
        });
    }

    /// <summary>The one gap that does not wait on endpoint evidence is recorded separately.</summary>
    [Fact]
    public void TheDummyPathIsTheIndependentOne()
    {
        // internal const, so read it the same way as the counts rather than depending on friend access
        var gap = (string)typeof(AddToCartCoverage)
            .GetField("IndependentGap", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!;

        Assert.Equal("AddToCartDummy", gap);
        Assert.False(AddToCartCoverage.IsImplemented(gap));
        Assert.False(AddToCartCoverage.HasSurfaceWithoutStep(gap));

        var row = Rows().Single(r => r.Name == "AddToCartDummy");
        Assert.Contains("no endpoint evidence", row.Note);
    }

    /// <summary>An unknown name is not implemented, and the answer is false rather than an exception.</summary>
    [Theory]
    [InlineData("AddToCart")]
    [InlineData("AddToCartBox")]
    [InlineData("AddToCartGraphQL")]
    public void ImplementedNamesAnswerTrue(string name)
    {
        Assert.True(AddToCartCoverage.IsImplemented(name));
    }

    [Theory]
    [InlineData("AddToCartZz")]
    [InlineData("")]
    [InlineData(null)]
    public void UnknownNamesAnswerFalse(string? name)
    {
        Assert.False(AddToCartCoverage.IsImplemented(name));
        Assert.False(AddToCartCoverage.HasSurfaceWithoutStep(name));
    }
}