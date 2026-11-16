using System.IO;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The six Vans paths, pinned against the image, together with the limit of what their recovery establishes.
///
/// <para>
/// R898. R896 measured www.vans.com at zero of three families and R897 established the store is represented — a site
/// id in <see cref="DemandwareControllers"/> and two assertions in DemandwareControllerTests — while its REST
/// endpoints were absent entirely. This round recovered the six path literals.
/// </para>
///
/// <para>
/// The tests below deliberately pin the <i>weak</i> claim as well as the paths. Ownership is family-level, not
/// path-level, and a future round that starts calling these as though Vans's ownership were observed should have to
/// delete a test that says otherwise.
/// </para>
/// </summary>
public class VansEndpointTests
{
    [Fact]
    public void SixPathsWereRecovered()
    {
        Assert.Equal(6, VansEndpoints.All.Count);
        Assert.Equal(6, VansEndpoints.All.Distinct().Count());
    }

    /// <summary>Both cart versions exist in the image, so neither can be dropped as a duplicate.</summary>
    [Fact]
    public void BothCartVersionsArePresent()
    {
        Assert.Contains("/cart/v1/cart/", VansEndpoints.All);
        Assert.Contains("/cart/v2/cart/", VansEndpoints.All);
    }

    /// <summary>
    /// The order endpoint appears twice, once as a path and once with a locale query. Keeping both records that the
    /// image has two spellings rather than one, which matters if a step needs the locale form.
    /// </summary>
    [Fact]
    public void TheOrderEndpointHasTwoSpellings()
    {
        Assert.Contains("/cart/v2/checkout/order/", VansEndpoints.All);
        Assert.Contains("/cart/v2/checkout/order?locale=", VansEndpoints.All);
    }

    /// <summary>
    /// The doubled word is in the image, not a slip in this file. Asserted so a later tidy-up cannot "fix" it into a
    /// path no server answers.
    /// </summary>
    [Fact]
    public void TheProductsPathReallyRepeatsItsWord()
    {
        Assert.Contains("/products/v2/products/", VansEndpoints.All);
    }

    /// <summary>
    /// Ownership is family-level: R893 associated the three families with www.vans.com, but none of these six
    /// literals carries a host of its own. Pinned as a fact so it cannot be quietly upgraded.
    /// </summary>
    [Fact]
    public void OwnershipIsRecordedAsInferenceNotObservation()
    {
        Assert.True(VansEndpoints.OwnershipIsInference);
        Assert.Equal("www.vans.com", VansEndpoints.FamilyHost);
    }

    /// <summary>
    /// Every path begins with one of the three families R893 associated with the host. A path whose family segment
    /// was mistyped would still compile and would still look plausible, so the family prefix is checked rather than
    /// assumed.
    /// </summary>
    [Fact]
    public void EveryPathStartsWithOneOfTheThreeFamilies()
    {
        var families = new[] { "/cart/v1/", "/cart/v2/", "/products/v2/" };

        foreach (var p in VansEndpoints.All)
            Assert.True(families.Any(p.StartsWith), p + " is not under any of the three recovered families");
    }
}
