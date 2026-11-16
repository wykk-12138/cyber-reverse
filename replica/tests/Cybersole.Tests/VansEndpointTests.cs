using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The six Vans paths, pinned against the image, plus the correction that R899 made to R898's version of them.
///
/// <para>
/// R898 recovered the same six paths without their <c>/api</c> prefix, because its scan pattern started matching at
/// the segment after <c>/api</c>. It also recorded ownership as inference, because none of the literals it looked at
/// carried a host — which was a second consequence of the same pattern. Searching for host and path together found
/// five literals holding both, so R899 both restored the prefix and settled the ownership question.
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

    /// <summary>
    /// The defect R898 introduced: every path in the image carries <c>/api</c>, and a constant without it names an
    /// endpoint no Vans server answers. Pinned so the prefix cannot be dropped again by a scan that starts too late.
    /// </summary>
    [Fact]
    public void EveryPathCarriesTheApiPrefix()
    {
        foreach (var p in VansEndpoints.All)
            Assert.StartsWith("/api/", p);
    }

    /// <summary>Both cart versions exist in the image, so neither can be dropped as a duplicate.</summary>
    [Fact]
    public void BothCartVersionsArePresent()
    {
        Assert.Contains("/api/cart/v1/cart/", VansEndpoints.All);
        Assert.Contains("/api/cart/v2/cart/", VansEndpoints.All);
    }

    /// <summary>
    /// The order endpoint appears twice, once as a path and once with a locale query. Keeping both records that the
    /// image has two spellings rather than one.
    /// </summary>
    [Fact]
    public void TheOrderEndpointHasTwoSpellings()
    {
        Assert.Contains("/api/cart/v2/checkout/order/", VansEndpoints.All);
        Assert.Contains("/api/cart/v2/checkout/order?locale=", VansEndpoints.All);
    }

    /// <summary>
    /// The doubled word is in the image, not a slip in this file, and it survives the prefix correction. Asserted so a
    /// later tidy-up cannot "fix" it into a path no server answers.
    /// </summary>
    [Fact]
    public void TheProductsPathReallyRepeatsItsWord()
    {
        Assert.Contains("/api/products/v2/products/", VansEndpoints.All);
    }

    /// <summary>
    /// Ownership is now observed: five literals hold the host and the path together. The flag was true one round
    /// earlier and its flip is the point, so it is asserted in the false direction rather than dropped.
    /// </summary>
    [Fact]
    public void OwnershipIsNoLongerInference()
    {
        Assert.False(VansEndpoints.OwnershipIsInference);
        Assert.Equal("www.vans.com", VansEndpoints.FamilyHost);
    }

    /// <summary>
    /// Every path begins with one of the three families R893 associated with the host, now with the api prefix in
    /// front. A path whose family segment was mistyped would still compile and would still look plausible.
    /// </summary>
    [Fact]
    public void EveryPathStartsWithOneOfTheThreeFamilies()
    {
        var families = new[] { "/api/cart/v1/", "/api/cart/v2/", "/api/products/v2/" };

        foreach (var p in VansEndpoints.All)
            Assert.True(families.Any(p.StartsWith), p + " is not under any of the three recovered families");
    }
}
