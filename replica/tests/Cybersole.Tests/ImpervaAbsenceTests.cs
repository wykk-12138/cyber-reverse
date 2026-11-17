using System.Linq;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1021: Imperva is absent on two independent counts, and this pins both so the claim stays checkable.
///
/// <para>
/// The first count is the artifact: none of the vendor's six spellings appears in it. The second is the vendor
/// inventory this workspace extracted from that artifact -- eight vendors, each carrying the literals that prove it --
/// which does not list Imperva at all, not even under "named but not handled". Two sources built at different times
/// agreeing is the standard AGENTS.md §2.7 sets, and it is what lets <c>Gap.VendorAbsent</c> mean something stronger
/// than "I did not find it".
/// </para>
/// </summary>
public sealed class ImpervaAbsenceTests
{
    /// <summary>The vendor inventory does not list it, in either list.</summary>
    [Fact]
    public void TheVendorInventoryDoesNotListImperva()
    {
        Assert.DoesNotContain(AntiBotVendors.All,
            v => v.Name.Contains("imperva", System.StringComparison.OrdinalIgnoreCase));
        Assert.DoesNotContain(AntiBotVendors.NamedButNotHandled,
            v => v.Name.Contains("imperva", System.StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// Every vendor that is listed carries evidence, which is what makes its absence meaningful: the inventory only
    /// counts a vendor it can point at a literal for.
    /// </summary>
    [Fact]
    public void EveryListedVendorCarriesEvidence()
    {
        Assert.NotEmpty(AntiBotVendors.All);
        foreach (var vendor in AntiBotVendors.All)
            Assert.False(string.IsNullOrWhiteSpace(vendor.Name) || vendor.Evidence.Count == 0,
                $"vendor {vendor.Name} has no evidence");
    }

    /// <summary>
    /// The detection branch survives as an extension, and the row records that rather than implying the image has it.
    /// </summary>
    [Fact]
    public void TheBranchIsRecordedAsAnExtension()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("_Incapsula_Resource", doc);
        Assert.Contains("this branch is an extension, not the image's behaviour", doc);
        Assert.Contains("six spellings is in the artifact", doc);

        var row = VendorWiring.Rows.Single(r => r.Vendor == "imperva");
        Assert.Equal(VendorWiring.Gap.VendorAbsent, row.Gap);
        Assert.Contains("two independent sources", row.Note);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        return dir?.FullName ?? System.AppContext.BaseDirectory;
    }
}
