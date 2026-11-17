using System.Linq;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1001: the four payment hosts the coverage table listed as unmatched now have gateways, and each one's endpoint is the
/// literal the image carries rather than a guessed shape.
///
/// <para>
/// What these tests hold is narrower than "the payment works". Mollie, GMO, Touchtech and Midtrans each had exactly one
/// path captured, so one step per gateway calls that path and the others say the endpoint was not captured. A made-up
/// path fails at the far end and comes back looking like the store declined us, which is the failure mode R823 named and
/// R991 removed from the token fallback.
/// </para>
/// </summary>
public sealed class UnmatchedGatewaysTests
{
    private static readonly string[] Added = { "mollie", "gmo", "touchtech", "midtrans" };

    /// <summary>All four are in the default registry, which is the call site that makes them reachable.</summary>
    [Fact]
    public void TheFourAreRegistered()
    {
        var registry = PaymentGatewayRegistry.CreateDefault();
        var ids = registry.All.Select(g => g.Id).ToList();

        foreach (var id in Added)
            Assert.Contains(id, ids);
    }

    /// <summary>Registration is what puts a gateway in the artifact, so the count matters as much as the names.</summary>
    [Fact]
    public void TheRegistryHasThirteen()
    {
        Assert.Equal(13, PaymentGatewayRegistry.CreateDefault().All.Count);
    }

    /// <summary>
    /// The steps the image says nothing about report that, rather than inventing an endpoint.
    ///
    /// <para>
    /// Midtrans is the exception and says so in its own message: Snap session creation is its tokenising step, so asking
    /// it to tokenise separately would be asking for something the protocol does not have.
    /// </para>
    /// </summary>
    [Fact]
    public void TheUncapturedStepsSaySo()
    {
        var registry = PaymentGatewayRegistry.CreateDefault();

        foreach (var id in new[] { "mollie", "gmo", "touchtech" })
        {
            var gateway = registry.Resolve(id);
            Assert.NotNull(gateway);

            var result = gateway!.TokenizeAsync(null!, default).GetAwaiter().GetResult();
            Assert.False(result.Ok);
            Assert.Contains("not captured", result.Error);
        }
    }

    /// <summary>Midtrans records both Snap versions the image names, so the older one need not be re-captured.</summary>
    [Fact]
    public void MidtransKeepsBothSnapVersions()
    {
        Assert.Equal(new[] { "/snap/v1/transactions", "/snap/v2/transactions" }, MidtransGateway.SnapPaths);
    }
}
