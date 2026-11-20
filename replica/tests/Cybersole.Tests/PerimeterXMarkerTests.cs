using System.Linq;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1022: PerimeterX is the mirror image of Imperva. The vendor is present -- four literals in the inventory -- and not
/// one of them can be grepped out of a response body, which is why its gap is <see cref="VendorWiring.Gap.NoPageMarker"/>
/// and not the "vendor absent" kind (docs/VENDOR_WIRING.md §10).
///
/// <para>
/// That distinction was asserted from one query until now. The inventory entry is the second witness, and it only
/// counts because each literal can be classified: five hits of "PerimeterX" are this workspace's own narration, the
/// token is a cookie name, the handler is a class name, and <c>_pxHandler</c> is a field. None is HTML.
/// </para>
/// </summary>
public sealed class PerimeterXMarkerTests
{
    /// <summary>
    /// The inventory entry is the five literals the classification rests on.
    ///
    /// <para>
    /// R1023: it was four. The query behind R1022 took the first four matches of the display name and stopped, so it
    /// never saw "Solving PerimeterX" at 0x146e9423c -- present progressive, and the one literal of the five that says
    /// the original solves this vendor rather than only routing around it. That retracts R1022's guess that switching
    /// proxies was its whole response.
    /// </para>
    /// </summary>
    [Fact]
    public void TheInventoryEntryIsTheFiveClassifiedLiterals()
    {
        var vendor = AntiBotVendors.All.Single(v => v.Name == "PerimeterX");

        Assert.Equal(
            new[] { "PerimeterX", "PerimeterX-Token", "PerimeterXHandler", "_pxHandler", "Solving PerimeterX" },
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

    // R1278: the two assertions that used to sit here read the audit table's Rows to check the gap kind, the marker
    // source and that both gap kinds have a live example. Those are rows in the audit table, which now lives in
    // docs/VENDOR_WIRING.md; what stays in this file is what the runtime inventory can be asked about.
}
