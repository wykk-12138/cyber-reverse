using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1227: the two place-order query shapes the Demandware submit builds, decoded from <c>sub_140A729F0</c>.
///
/// <para>
/// The replica already had the controller name <c>CheckoutServices-PlaceOrder</c> but neither query variant:
/// <c>termsconditions</c> and <c>DFReferenceId</c> both returned no match under <c>replica/src</c> before this
/// round. The fingerprint variant is how a Cardinal 3-D Secure device fingerprint reaches a Demandware checkout,
/// and the other variant's value is the literal <c>undefined</c> rather than an empty string, which is the kind of
/// storefront quirk that has to be copied rather than tidied.
/// </para>
/// </summary>
public sealed class DemandwarePlaceOrderQueryTests
{
    [Fact]
    public void WithAFingerprintTheQueryCarriesBothTermsAndTheReference()
    {
        Assert.Equal(
            "/CheckoutServices-PlaceOrder?termsconditions=true&DFReferenceId=df-1",
            DemandwareControllers.PlaceOrderPathWith("df-1"));
    }

    [Fact]
    public void WithoutAFingerprintTheValueIsTheLiteralUndefined()
    {
        Assert.Equal("/CheckoutServices-PlaceOrder?termsconditions=undefined",
            DemandwareControllers.PlaceOrderPathWith(null));
        Assert.Equal("/CheckoutServices-PlaceOrder?termsconditions=undefined",
            DemandwareControllers.PlaceOrderPathWith(string.Empty));
    }

    [Fact]
    public void TheReferenceIsEscaped()
    {
        Assert.EndsWith("DFReferenceId=a%2Fb%26c", DemandwareControllers.PlaceOrderPathWith("a/b&c"));
    }

    [Fact]
    public void TheTwoQueryLiteralsAreVerbatim()
    {
        Assert.Equal("?termsconditions=true&DFReferenceId=", DemandwareControllers.PlaceOrderQueryWithFingerprint);
        Assert.Equal("?termsconditions=undefined", DemandwareControllers.PlaceOrderQueryWithoutFingerprint);
    }
}
