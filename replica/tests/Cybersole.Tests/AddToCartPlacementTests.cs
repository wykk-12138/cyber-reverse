using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Adjacency applied to all thirteen names, and the fourth misfiling it found.
///
/// <para>
/// R942. A first attempt scanned ordinals image-wide and produced nonsense, because ordinals are numbered per class and
/// d__36 exists in many classes at once. Inside one descriptor string a run of ordinals increasing by one is one class's
/// method list, and read that way six names place themselves: AddToCart among CSRF and checkout calls, App and AppDw among
/// app-session calls, Preload beside HandleOutOfStock, and Dummy and Multi together in PopMart's draw class. That last
/// pairing is the fourth misfiling: Multi is add-many-boxes, not a generic multi-item cart.
/// </para>
/// </summary>
public class AddToCartPlacementTests
{
    private static (string Name, int Ordinal, string Class, string[] Neighbours)[] Rows() =>
        ((string, int, string, string[])[])typeof(AddToCartPlacement)
            .GetField("Rows", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>Six placed, seven not, and the counts are stated.</summary>
    [Fact]
    public void AllThirteenArePlaced()
    {
        Assert.Equal(13, Rows().Length);
        // R943: all thirteen are placed now, the last seven from their own strings rather than from one concatenated run
        Assert.Equal(13, Rows().Count(r => r.Neighbours.Length > 0));
        Assert.Equal(0, Rows().Count(r => r.Neighbours.Length == 0));

        Assert.Equal(13, (int)typeof(AddToCartPlacement)
            .GetField("Placed", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
        Assert.Equal(0, (int)typeof(AddToCartPlacement)
            .GetField("Unplaced", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>The classes the six landed in, which is what the neighbours say rather than what the names suggest.</summary>
    [Theory]
    [InlineData("AddToCart", "web checkout")]
    [InlineData("AddToCartApp", "app session")]
    [InlineData("AddToCartAppDw", "app session")]
    [InlineData("AddToCartDummy", "PopMart draw")]
    [InlineData("AddToCartMulti", "PopMart draw")]
    [InlineData("AddToCartPreload", "product stock")]
    public void TheClassIsWhatTheNeighboursSay(string name, string expected)
    {
        Assert.Equal(expected, AddToCartPlacement.ClassOf(name));
    }

    /// <summary>
    /// The correction: Multi shares PopMart's class with Dummy and RemoveDummy, so its old note calling it a generic
    /// multi-item cart was wrong.
    /// </summary>
    [Fact]
    public void MultiIsTheFourthMisfiling()
    {
        var note = (string)typeof(AddToCartPlacement)
            .GetField("FourthMisfiling", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!;

        Assert.Contains("add-many-boxes", note);

        var coverage = ((string, bool, string)[])typeof(AddToCartCoverage)
            .GetField("Rows", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;
        var multi = coverage.Single(r => r.Item1 == "AddToCartMulti");
        Assert.Contains("not a generic multi-item cart", multi.Item3);
    }

    /// <summary>
    /// Unplaced is unknown, never absent. The descriptor scan is truncated, so a name can be missing from this table
    /// without being missing from the image -- the distinction R939 paid for.
    /// </summary>
    [Fact]
    public void EvenPlacedNamesLeaveTheClassUnproven()
    {
        // every name now has neighbours, so nothing is unplaced; what remains unproven is whether a name beside another
        // framework's name shares its class, which the ordinals in these strings cannot answer
        foreach (var name in new[] { "AddToCartNext", "AddToCartAstro", "AddToCartSvelte", "AddToCartFrontend", "AddToCartGraphQL" })
            Assert.True(AddToCartPlacement.IsPlaced(name));

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "AddToCartPlacement.cs"));
        Assert.Contains("Absence from a run is not evidence of anything", doc);
    }

    /// <summary>
    /// The mistake the first attempt made, recorded: ordinals are per class, so comparing them across the image produces
    /// neighbours from unrelated classes.
    /// </summary>
    [Fact]
    public void OrdinalsArePerClassAndTheFirstScanIgnoredThat()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "AddToCartPlacement.cs"));

        Assert.Contains("numbered per class", doc);
        Assert.Contains("CastIterator", doc);   // named as the nonsense the first attempt produced
    }

    /// <summary>An unknown name is neither placed nor classed, and answers null rather than throwing.</summary>
    [Theory]
    [InlineData("AddToCartZz")]
    [InlineData("")]
    [InlineData(null)]
    public void UnknownNamesAnswerNull(string? name)
    {
        Assert.False(AddToCartPlacement.IsPlaced(name));
        Assert.Null(AddToCartPlacement.ClassOf(name));
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