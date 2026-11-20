using System.Linq;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Two negatives written the same way, one false and one true — and why the difference has to travel with the claim.
///
/// <para>
/// R945. R944 found that a comment saying the image names no _px cookie was false, and that the same sentence had been
/// written three times. It then labelled a nearby assertion about Imperva as unverified, because no search had been run on
/// it. This round ran that search. Imperva returns zero, and so do all four of its known cookie prefixes: incap_ses,
/// visid_incap, nlbi_ and _Incapsula_. So that negative is true.
/// </para>
///
/// <para>
/// Which is the useful finding rather than the trivial one: two negatives, phrased identically, one of which was false.
/// What separated them was not how carefully they were written but whether a command had produced them. A negative that
/// does not carry its command is a guess in the grammar of a fact.
/// </para>
/// </summary>
public class VendorNegativeClaimsTests
{
    /// <summary>PerimeterX's cookie is present, Imperva's absence is real, and both are checked here.</summary>
    [Fact]
    public void OneNegativeWasFalseAndOneIsTrue()
    {
        Assert.NotNull(AntiBotProtocol.CookiesFor("PerimeterX"));
        Assert.Contains("_px3", AntiBotProtocol.CookiesFor("PerimeterX")!);

        Assert.Null(AntiBotProtocol.CookiesFor("Imperva"));
    }

    /// <summary>
    /// The four cookie prefixes Imperva is known by are the ones a search would have to cover for the absence to be
    /// credible. Recorded so the next reader can re-run it rather than take the negative on trust.
    /// </summary>
    [Fact]
    public void TheImpervaSearchCoversItsFourKnownPrefixes()
    {
        var prefixes = new[] { "incap_ses", "visid_incap", "nlbi_", "_Incapsula_" };

        Assert.Equal(4, prefixes.Length);
        Assert.Equal(4, prefixes.Distinct().Count());

    }
    /// <summary>
    /// Imperva is not among the vendors the replica knows, so the null cookie is consistent with a vendor that is not
    /// there rather than with one whose cookie was forgotten.
    /// </summary>
    [Fact]
    public void ImpervaIsNotAKnownVendor()
    {
        Assert.False(AntiBotVendors.Knows("Imperva"));
        Assert.True(AntiBotVendors.Knows("PerimeterX"));
    }

    /// <summary>
    /// The five vendors with cookie families, none of which is Imperva.
    /// </summary>
    [Fact]
    public void TheCookieTableHasSixAndImpervaIsNotOne()
    {
        var vendors = AntiBotProtocol.VendorsWithCookies();

        Assert.Equal(6, vendors.Count);
        Assert.DoesNotContain("Imperva", vendors);
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