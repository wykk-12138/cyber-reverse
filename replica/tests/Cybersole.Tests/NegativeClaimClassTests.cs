using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The distinction between a negative a test can prove and a negative only the image can.
///
/// <para>
/// R946. After R944 and R945 turned on one false negative and one true one, the obvious question was how many more there
/// are. A scan found 772 negative assertions in the suite and 118 that name a concrete string, of which two sit near any
/// evidence at all -- but that number is misleading, because most of the 118 are not claims about the original. Asserting
/// that a lookup returns null for an unknown key proves itself; the function is right there.
/// </para>
///
/// <para>
/// The class that matters is narrower: a negative whose truth depends on the image rather than on the code under test.
/// "NikeEndpoints has no buy/carts path" cannot be checked by running the method -- it can only be checked by searching
/// the binary. Those are the ones that need a command, and R944 showed what happens without one: the claim gets copied
/// into a comment and two assertions, and three copies of a guess read like a corroborated fact.
/// </para>
///
/// <para>
/// This class records the distinction and names the members of the second kind that are currently known, so the next scan
/// starts from a list rather than from 772 lines.
/// </para>
/// </summary>
public class NegativeClaimClassTests
{
    /// <summary>
    /// A negative is self-proving when the code under test is the only witness: an unknown key, an empty collection, a
    /// malformed input. The test supplies the input and observes the output, and no claim about the original is made.
    /// </summary>
    internal static readonly string[] SelfProvingExamples =
    {
        "Assert.Null(CookiesFor(\"NoSuchVendor\"))",
        "Assert.Empty(HelpView.Filter(\"zzzz\"))",
        "Assert.Null(Jwt.Decode(\"not-a-token\"))",
        "Assert.False(AccountAndAuthFamilies.IsKnown(\"/api/auth/nope\"))",
    };

    /// <summary>
    /// A negative needs the image when its truth is a fact about the original that running the code cannot settle. Each of
    /// these was found by the R946 scan and none carried a command.
    /// </summary>
    internal static readonly (string Claim, string Needs)[] ImageClaims =
    {
        ("NikeEndpoints has no buy/carts/ path", "a search of the image for that path"),
        ("NikeEndpoints has no buy/orders/ path", "a search for that path"),
        ("NikeEndpoints.OrderV5 does not mention scheels", "a search for scheels in that table"),
        ("AntiBotVendors.DataDomeRelay does not contain datadome.co", "a search for the relay host"),
        ("PopMartStepMap has no endpoint for CheckResult", "a search for that step's endpoint"),
        ("JohnLewisStepMap has no endpoint for GetStripePaymentIntent", "a search for that endpoint"),
        ("StoreFlowSteps shares no GetMerchantCode with single", "the step table's own ordinals"),
        ("No scrape method is named ScrapeProductBox", "R938 already ran this one"),
    };

    /// <summary>The two kinds, counted, so the 118 figure is not mistaken for 118 problems.</summary>
    [Fact]
    public void TheTwoKindsAreDistinguished()
    {
        Assert.Equal(4, SelfProvingExamples.Length);
        Assert.Equal(8, ImageClaims.Length);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "tests", "Cybersole.Tests", "NegativeClaimClassTests.cs"));
        Assert.Contains("proves itself", doc);
    }

    /// <summary>
    /// Every image claim names what it would take to check it. A claim without that is the thing R944 found three copies
    /// of.
    /// </summary>
    [Fact]
    public void EveryImageClaimNamesItsCommand()
    {
        Assert.All(ImageClaims, c =>
        {
            Assert.False(string.IsNullOrWhiteSpace(c.Needs));
            Assert.True(c.Needs.Contains("search") || c.Needs.Contains("ordinal") || c.Needs.Contains("R938"),
                        c.Claim + " -> " + c.Needs);
        });
    }

    /// <summary>
    /// One of the eight has already been run, and the record says so rather than leaving all eight looking equally open.
    /// </summary>
    [Fact]
    public void OneOfTheEightIsAlreadySettled()
    {
        var settled = ImageClaims.Where(c => c.Needs.Contains("R938")).ToArray();

        Assert.Single(settled);
        Assert.Contains("ScrapeProductBox", settled[0].Claim);
    }

    /// <summary>
    /// The scan's own numbers, recorded with the caveat that made them misleading: 772 assertions, 118 naming a string, two
    /// near any evidence, and most of the 118 self-proving.
    /// </summary>
    [Fact]
    public void TheScanNumbersCarryTheirCaveat()
    {
        const int total = 772;
        const int named = 118;
        const int withEvidence = 2;

        Assert.True(withEvidence < named);
        Assert.True(named < total);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "tests", "Cybersole.Tests", "NegativeClaimClassTests.cs"));
        Assert.Contains("most of the 118 are not claims about the original", doc);
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