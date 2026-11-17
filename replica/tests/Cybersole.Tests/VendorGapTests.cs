using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1020: two rows said <c>Inferred</c> for opposite reasons, and the table could not tell them apart.
///
/// <para>
/// imperva appears in the artifact under none of its six spellings, so there is no vendor to look for. perimeterx is
/// present, with four cookie-side literals, and just has nothing page-level to grep for. Those lead to different next
/// moves -- establish whether the original handles Imperva at all, or find a marker for a vendor it demonstrably
/// handles -- and a reader scanning the audit used to see one word for both.
/// </para>
/// </summary>
public sealed class VendorGapTests
{
    /// <summary>The two inferred rows carry different reasons, and only those two carry any.</summary>
    [Fact]
    public void TheTwoInferredRowsSayWhyTheyAreInferred()
    {
        var byVendor = VendorWiring.Rows.ToDictionary(r => r.Vendor, r => r.Gap);

        Assert.Equal(VendorWiring.Gap.VendorAbsent, byVendor["imperva"]);
        Assert.Equal(VendorWiring.Gap.NoPageMarker, byVendor["perimeterx"]);

        // every other row has no gap at all: its marker is the image's
        var others = VendorWiring.Rows
            .Where(r => r.Vendor != "imperva" && r.Vendor != "perimeterx")
            .ToList();
        Assert.All(others, r => Assert.Equal(VendorWiring.Gap.None, r.Gap));
    }

    /// <summary>A row marked None must actually be an image literal, or the two columns disagree.</summary>
    [Fact]
    public void NoGapImpliesAnImageLiteral()
    {
        foreach (var row in VendorWiring.Rows.Where(r => r.Gap == VendorWiring.Gap.None))
            Assert.Equal(VendorWiring.MarkerSource.ImageLiteral, row.MarkerFrom);
    }

    /// <summary>And a gap implies the marker is not the image's, in the other direction.</summary>
    [Fact]
    public void AGapImpliesAnInferredMarker()
    {
        foreach (var row in VendorWiring.Rows.Where(r => r.Gap != VendorWiring.Gap.None))
            Assert.Equal(VendorWiring.MarkerSource.Inferred, row.MarkerFrom);
    }

    /// <summary>
    /// The column is only worth having if it survives a reader asking for it in one place, so the audit can render the
    /// split rather than leaving it in prose.
    /// </summary>
    [Fact]
    public void TheAuditCanBeGroupedByReason()
    {
        var absent = VendorWiring.Rows.Where(r => r.Gap == VendorWiring.Gap.VendorAbsent).Select(r => r.Vendor).ToList();
        var noMarker = VendorWiring.Rows.Where(r => r.Gap == VendorWiring.Gap.NoPageMarker).Select(r => r.Vendor).ToList();

        Assert.Equal(new[] { "imperva" }, absent);
        Assert.Equal(new[] { "perimeterx" }, noMarker);
    }
}
