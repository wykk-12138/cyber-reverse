using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Astro pages, whose whole recovered handle is the attribute prefix data-astro-cid and a family of method names.
///
/// <para>
/// R935. The obvious guess was Astro's island mechanism -- astro-island elements with a props attribute -- and searching
/// for it returned nothing, which is what made the one literal that does exist findable: data-astro-cid. Astro stamps
/// every rendered element with that prefix plus a per-build suffix to scope its styles, so the suffix cannot be
/// hard-coded and the attribute has to be matched by prefix. These tests pin the prefix, the family, and the fact that
/// an empty answer means "no cid attribute on this page", not "not an Astro page".
/// </para>
/// </summary>
public class AstroSurfaceTests
{
    private static string Const(string name) =>
        (string)typeof(AstroSurface)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    /// <summary>The one literal, and the method family that explains why an attribute exists beside the props.</summary>
    [Fact]
    public void ThePrefixAndTheMethodFamilyAreRecorded()
    {
        Assert.Equal("data-astro-cid", Const("CidPrefix"));

        var family = (string[])typeof(AstroSurface)
            .GetField("MethodFamily", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(7, family.Length);
        Assert.Contains("AddToCartAstro", family);
        Assert.Contains("ParseAstroProduct", family);
        // parse methods carry Astro in the middle -- ParseAstroProduct -- so containment is the right test, not a
        // suffix. The suffix form only holds for the actions, which are named after the step they perform.
        Assert.All(family, name => Assert.Contains("Astro", name));
    }

    /// <summary>Distinct attributes in order, since a page usually carries more than one scope.</summary>
    [Fact]
    public void AttributesAreDistinctAndInOrder()
    {
        var html = "<div data-astro-cid-abc123 class=\"a\"><span data-astro-cid-def456>x</span>" +
                   "<b data-astro-cid-abc123>y</b></div>";

        var attrs = AstroSurface.Attributes(html);

        Assert.Equal(new[] { "data-astro-cid-abc123", "data-astro-cid-def456" }, attrs);
    }

    /// <summary>The suffix is not hard-coded, so a different build's attribute is still recognised.</summary>
    [Theory]
    [InlineData("data-astro-cid-zz9")]
    [InlineData("data-astro-cid-a_b-1")]
    [InlineData("data-astro-cid-XYZ")]
    public void AnySuffixIsRecognised(string attribute)
    {
        Assert.True(AstroSurface.LooksLikeAstro("<p " + attribute + ">t</p>"));
    }

    /// <summary>
    /// A near miss does not match: the pattern is anchored on a hyphen after the prefix, so a name that merely starts
    /// with the same letters is not taken for a cid.
    /// </summary>
    [Fact]
    public void ANearMissIsNotACid()
    {
        Assert.False(AstroSurface.LooksLikeAstro("<p data-astro-cidx>t</p>"));
        Assert.False(AstroSurface.LooksLikeAstro("<p data-astrocid-abc>t</p>"));
    }

    /// <summary>
    /// An empty answer is "no cid attribute here", which is not the same as "not an Astro page" -- scoped styles can be
    /// stripped. Asserted so the weaker claim is the one the code makes.
    /// </summary>
    [Fact]
    public void NoAttributeIsNotProofOfNotAstro()
    {
        Assert.False(AstroSurface.LooksLikeAstro("<html></html>"));
        Assert.Empty(AstroSurface.Attributes(null));

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "AstroSurface.cs"));
        Assert.Contains("A false answer is not proof of the opposite", doc);
    }

    /// <summary>Tags bearing a given attribute are returned whole, so a caller can see which element a scope is on.</summary>
    [Fact]
    public void TagsBearingAnAttributeAreReturned()
    {
        var html = "<div data-astro-cid-abc>1</div><section data-astro-cid-abc class=\"s\">2</section>";

        var tags = AstroSurface.TagsWith(html, "data-astro-cid-abc");

        Assert.Equal(2, tags.Count);
        Assert.StartsWith("<div", tags[0]);
        Assert.Contains("class=\"s\"", tags[1]);
    }

    /// <summary>
    /// The island mechanism was searched for and is absent from the image, so it must not be claimed here. Pinned as a
    /// fact about the source rather than about the binary, so the note cannot quietly become an assumption.
    /// </summary>
    [Fact]
    public void TheIslandMechanismIsNotClaimed()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "AstroSurface.cs"));

        Assert.Contains("astro-island", doc);   // named only to say it is absent
        Assert.DoesNotContain("AstroIsland", doc);
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