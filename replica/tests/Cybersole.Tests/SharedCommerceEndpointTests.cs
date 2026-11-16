using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The eleven residual hostless paths and the two facts that make them useful: that their owner is unknown, and that
/// two of them belong to the anti-bot priority rather than to a checkout flow.
///
/// <para>
/// R903. R902 closed the account family; this closes the rest of the hostless set, which together is every path with
/// no owning store that R901's canonical measurement found. With these, the hostless bucket should contain no missing
/// rows.
/// </para>
/// </summary>
public class SharedCommerceEndpointTests
{
    [Fact]
    public void ElevenPathsWereRecovered()
    {
        Assert.Equal(11, SharedCommerceEndpoints.All.Count);
        Assert.Equal(SharedCommerceEndpoints.RecoveredPathCount, SharedCommerceEndpoints.All.Count);
        Assert.Equal(11, SharedCommerceEndpoints.All.Distinct().Count());
    }

    /// <summary>The owner is unknown for all eleven, and that is the class's central claim.</summary>
    [Fact]
    public void TheOwningStoreIsRecordedAsUnknown()
    {
        Assert.True(SharedCommerceEndpoints.OwnerIsUnknown);
    }

    /// <summary>
    /// The shield path and the 3DS fingerprint are the anti-bot priority's share of this set. Named as a separate list
    /// so that priority can be counted without re-reading every path in the class.
    /// </summary>
    [Fact]
    public void TwoPathsBelongToTheAntiBotPriority()
    {
        Assert.Equal(2, SharedCommerceEndpoints.AntiBotRelated.Count);
        Assert.Contains("/shield/v1/verify_otp", SharedCommerceEndpoints.AntiBotRelated);
        Assert.Contains("/checkoutshopper/v1/submitThreeDS2Fingerprint?token=",
            SharedCommerceEndpoints.AntiBotRelated);
    }

    /// <summary>Every anti-bot path is also in the full set; a subset that drifted out would be invisible otherwise.</summary>
    [Fact]
    public void TheAntiBotSubsetIsContainedInTheWhole()
    {
        foreach (var p in SharedCommerceEndpoints.AntiBotRelated)
            Assert.Contains(p, SharedCommerceEndpoints.All);
    }

    /// <summary>
    /// Five platform words appear here that no other endpoint class uses -- bags for a cart, pdp for a product page,
    /// shield for protection, and the plural verificationcodes. Asserted so a later "normalise the naming" pass has to
    /// notice that they are the image's words rather than inconsistencies.
    /// </summary>
    [Fact]
    public void ThePlatformWordsArePreserved()
    {
        Assert.Contains("/commerce/v1/bags", SharedCommerceEndpoints.All);
        Assert.Contains("/product-core/v1/pdp", SharedCommerceEndpoints.All);
        Assert.Contains("/product-core/v1/pdp/sku", SharedCommerceEndpoints.All);
        Assert.Contains("/marketing/v1/verificationcodes", SharedCommerceEndpoints.All);
        Assert.Contains("/shield/v1/verify_otp", SharedCommerceEndpoints.All);
    }

    /// <summary>
    /// The fingerprint endpoint carries its token in the query, which means the fingerprint is an input rather than
    /// something this code computes. Pinned because a later refactor that "tidies" the query away would change who is
    /// responsible for producing it.
    /// </summary>
    [Fact]
    public void TheFingerprintTokenStaysInTheQuery()
    {
        var p = SharedCommerceEndpoints.ThreeDs2Fingerprint;
        Assert.Contains("?token=", p);
        Assert.EndsWith("?token=", p);
    }
}
