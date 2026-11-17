using System.Linq;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1022: PerimeterX is the mirror image of Imperva. The vendor is present -- four literals in the inventory -- and not
/// one of them can be grepped out of a response body, which is why its gap is <see cref="VendorWiring.Gap.NoPageMarker"/>
/// and not <see cref="VendorWiring.Gap.VendorAbsent"/>.
///
/// <para>
/// That distinction was asserted from one query until now. The inventory entry is the second witness, and it only
/// counts because each literal can be classified: five hits of "PerimeterX" are this workspace's own narration, the
/// token is a cookie name, the handler is a class name, and <c>_pxHandler</c> is a field. None is HTML.
/// </para>
/// </summary>
public sealed class PerimeterXMarkerTests
{
    /// <summary>The inventory entry is exactly the four literals the classification rests on.</summary>
    [Fact]
    public void TheInventoryEntryIsTheFourClassifiedLiterals()
    {
        var vendor = AntiBotVendors.All.Single(v => v.Name == "PerimeterX");

        Assert.Equal(new[] { "PerimeterX", "PerimeterX-Token", "PerimeterXHandler", "_pxHandler" },
            vendor.Evidence.ToArray());
    }

    /// <summary>None of those four is a string a store's page would contain.</summary>
    [Fact]
    public void NoneOfTheFourIsAPageLevelLiteral()
    {
        var pageLevel = new[] { "px-captcha", "captcha-delivery", "/interstitial/", "block" };
        var vendor = AntiBotVendors.All.Single(v => v.Name == "PerimeterX");

        foreach (var evidence in vendor.Evidence)
        foreach (var page in pageLevel)
            Assert.DoesNotContain(page, evidence, System.StringComparison.OrdinalIgnoreCase);
    }

    /// <summary>The row says which gap this is, and the note names the reason rather than leaving it to inference.</summary>
    [Fact]
    public void TheRowRecordsTheGapAsAMissingPageMarker()
    {
        var row = VendorWiring.Rows.Single(r => r.Vendor == "perimeterx");

        Assert.Equal(VendorWiring.Gap.NoPageMarker, row.Gap);
        Assert.Equal(VendorWiring.MarkerSource.Inferred, row.MarkerFrom);
        Assert.Equal("px-captcha", row.Marker);
    }

    /// <summary>
    /// The two gap kinds are carried by different vendors, so a reader can see both states in one table rather than
    /// having to trust that the taxonomy has two live cases.
    /// </summary>
    [Fact]
    public void BothGapKindsHaveALiveExample()
    {
        Assert.Equal(VendorWiring.Gap.VendorAbsent,
            VendorWiring.Rows.Single(r => r.Vendor == "imperva").Gap);
        Assert.Equal(VendorWiring.Gap.NoPageMarker,
            VendorWiring.Rows.Single(r => r.Vendor == "perimeterx").Gap);
    }
}
