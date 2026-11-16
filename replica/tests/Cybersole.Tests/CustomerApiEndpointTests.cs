using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The ten <c>/customer/v1/</c> account paths, and the fact that their owner is unknown.
///
/// <para>
/// R902. R901's canonical measurement listed these ten under the hostless bucket: they exist in the image, no literal
/// holding them also holds a host, and the replica had no <c>/customer/v1/</c> literal at all. So this is the case
/// where the endpoints are observed and the owning store is not, which is a wider gap than the Vans family, where
/// host and path shared a literal.
/// </para>
/// </summary>
public class CustomerApiEndpointTests
{
    [Fact]
    public void TenPathsWereRecovered()
    {
        Assert.Equal(10, CustomerApiEndpoints.All.Count);
        Assert.Equal(CustomerApiEndpoints.RecoveredPathCount, CustomerApiEndpoints.All.Count);
        Assert.Equal(10, CustomerApiEndpoints.All.Distinct().Count());
    }

    /// <summary>
    /// The ownership gap is the point of this class, so it is asserted rather than left in a comment. If a future
    /// round finds a literal holding one of these paths next to a host, it should flip this flag and say so.
    /// </summary>
    [Fact]
    public void TheOwningStoreIsRecordedAsUnknown()
    {
        Assert.True(CustomerApiEndpoints.OwnerIsUnknown);
    }

    /// <summary>Address handling is the four-verb set; a partial copy that dropped one would still compile.</summary>
    [Fact]
    public void TheAddressVerbsAreComplete()
    {
        foreach (var verb in new[] { "add", "del", "list", "update" })
            Assert.Contains("/customer/v1/address/" + verb, CustomerApiEndpoints.All);
    }

    /// <summary>
    /// Signup needs the existence check before the registration itself, and both spellings are in the image. Kept
    /// separate because a flow that only registered would double-create accounts.
    /// </summary>
    [Fact]
    public void TheSignupCheckAndTheRegistrationAreSeparate()
    {
        Assert.Contains("/customer/v1/customer/exist", CustomerApiEndpoints.All);
        Assert.Contains("/customer/v1/customer/register", CustomerApiEndpoints.All);
        Assert.Contains("/customer/v1/customer/guest/register", CustomerApiEndpoints.All);
    }

    [Fact]
    public void EveryPathIsUnderTheCustomerFamily()
    {
        foreach (var p in CustomerApiEndpoints.All)
            Assert.StartsWith("/customer/v1/", p);
    }

    /// <summary>
    /// The list is presented in the order a signup would use them, which is a claim about usage and not about the
    /// image. If it were sorted alphabetically this test would pass trivially; it checks the first entry is the
    /// existence probe so the ordering stays meaningful.
    /// </summary>
    [Fact]
    public void TheListIsOrderedForUseRatherThanAlphabetically()
    {
        Assert.Equal(CustomerApiEndpoints.CustomerExist, CustomerApiEndpoints.All.First());
        Assert.NotEqual(CustomerApiEndpoints.All.OrderBy(p => p, System.StringComparer.Ordinal),
            CustomerApiEndpoints.All);
    }
}
