using System.Linq;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Dicks Sporting Goods, added in R919 from nine literals: four identity forms, four endpoints and one behaviour.
///
/// <para>
/// The behaviour literal is the most informative — <c>_outOfStock</c> is a closure name, so the original attaches an
/// out-of-stock callback to this store specifically. And the endpoints are a product search by part number and a
/// paygate, with no cart or checkout path recovered at all, which is why the sequence stops at two steps.
/// </para>
/// </summary>
public class DicksSportingGoodsFlowTests
{
    private static string Const(string name)
    {
        var f = typeof(DicksSportingGoodsFlow).GetField(name, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        Assert.NotNull(f);
        return (string)f!.GetRawConstantValue()!;
    }

    /// <summary>
    /// Four identity forms are recorded rather than one chosen, because which appears in a request is unknown and a
    /// guess would put a wrong value in a header.
    /// </summary>
    [Fact]
    public void AllFourIdentityFormsAreRecorded()
    {
        Assert.Equal("DICKS", Const("ShortTag"));
        Assert.Equal("DicksSportingGoods", Const("IdForm"));
        Assert.Equal("Dicks Sporting Goods", Const("DisplayName"));
        Assert.Equal("dsg-ecomm", Const("Channel"));
    }

    /// <summary>
    /// Three hosts and four addresses, verbatim, so an edit that renames or drops one is visible.
    /// </summary>
    [Fact]
    public void TheFourRecoveredAddressesArePresent()
    {
        Assert.Equal("https://www.dickssportinggoods.com", Const("StorefrontHost"));
        Assert.Equal("https://api-search.dickssportinggoods.com", Const("SearchHost"));
        Assert.Equal("https://payments.dickssportinggoods.com", Const("PayHost"));

        Assert.Equal("/catalog-productdetails/v4/byPartNumber/", Const("ByPartNumber"));
        Assert.Equal("/prod/api/paygate/v2/authorization", Const("PayAuthorize"));
        Assert.Equal("/prod/api/paygate/v2/threeDSAuthentication", Const("PayThreeDs"));

        Assert.Equal(4, (int)typeof(DicksSportingGoodsFlow)
            .GetField("RecoveredAddressCount", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>
    /// Two steps, not a full purchase. A store with a paygate but no recovered basket call cannot be taken through a
    /// purchase from this evidence, and a longer sequence would be steps that fail at the second one.
    /// </summary>
    [Fact]
    public void TheSequenceStopsWhereTheEvidenceStops()
    {
        var flow = new DicksSportingGoodsFlow();
        Assert.Equal(new[] { "FindProduct", "SubmitPayment" }, flow.StepSequence);
        Assert.DoesNotContain("AddToCart", flow.StepSequence);
        Assert.DoesNotContain("SubmitOrder", flow.StepSequence);
    }

    /// <summary>The part number comes out of a product URL when the session has none.</summary>
    [Theory]
    [InlineData("https://www.dickssportinggoods.com/p/nike-air-max-1-abc123", "nike-air-max-1-abc123")]
    [InlineData("https://www.dickssportinggoods.com/product?partNumber=DSG-4412", "DSG-4412")]
    [InlineData("https://www.dickssportinggoods.com/", "")]
    public void ThePartNumberIsReadFromTheUrl(string url, string expected)
    {
        Assert.Equal(expected, (string)typeof(DicksSportingGoodsFlow).GetMethod("PartNumberFrom", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!.Invoke(null, new object[] { url })!);
    }

    /// <summary>Registered, so it is reachable by id and its hosts route to it.</summary>
    [Fact]
    public void ItIsRegisteredAndClaimsItsHosts()
    {
        var all = StoreModuleCatalog.CreateAll();
        Assert.Contains(all, m => m.Id == "dickssportinggoods");

        var flow = new DicksSportingGoodsFlow();
        Assert.Contains("www.dickssportinggoods.com", flow.Domains);
        Assert.Contains("api-search.dickssportinggoods.com", flow.Domains);
        Assert.Contains("payments.dickssportinggoods.com", flow.Domains);
    }

    /// <summary>
    /// The two paygate calls stay separate: a flow that always ran the 3-D Secure step would authenticate orders that
    /// needed no authentication. Asserted as source shape, since exercising it needs a live paygate.
    /// </summary>
    [Fact]
    public void ThreeDSecureIsConditional()
    {
        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(), "src", "Cybersole.Stores", "Flows", "DicksSportingGoodsFlow.cs"));

        Assert.Contains("requires?3DS", source);
        Assert.Contains("return StepOutcome.Success();", source);
        // the 3DS *call* sits after the conditional return, not before it. Looking for the constant name would have
        // found its declaration near the top of the file and asserted nothing about order.
        Assert.True(source.IndexOf("PayHost + PayThreeDs", System.StringComparison.Ordinal) >
                    source.IndexOf("requires?3DS", System.StringComparison.Ordinal));
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