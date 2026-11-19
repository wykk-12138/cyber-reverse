using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1250: the Magento REST paths the image carries, and the two the replica had assumed without evidence.
///
/// <para>
/// The flow audit left twenty-six paths with no hit and no neighbour; the Magento ones turned out not to be missing
/// from the image at all, but spelled differently: the image composes <c>/carts/mine/…</c> with a suffix per action
/// (items, coupons, payment-information, shipping-information, estimate-shipping-methods) and prefixes it either with
/// <c>/V1</c> or with <c>rest/{locale}/V1</c>, while the replica had built <c>/rest/V1/carts/mine</c> and
/// <c>/rest/V1/carts/mine/totals</c>, neither of which exists in the image in any casing.
/// </para>
/// </summary>
public sealed class MagentoRestTests
{
    [Fact]
    public void TheActionSuffixedPathsAreTheImagesOwn()
    {
        Assert.Equal("/carts/mine/payment-information", MagentoRest.PaymentInformation);
        Assert.Equal("/carts/mine/shipping-information", MagentoRest.ShippingInformation);
        Assert.Equal("/carts/mine/items/", MagentoRest.Items);
        Assert.Equal("/carts/mine/coupons/", MagentoRest.Coupons);
        Assert.EndsWith("?", MagentoRest.EstimateShippingMethods);
    }

    [Fact]
    public void TheV1PrefixedPairAndTheBarePairAreBothCarried()
    {
        Assert.Equal("/V1" + MagentoRest.PaymentInformation, MagentoRest.V1PaymentInformation);
        Assert.Equal("/V1" + MagentoRest.ShippingInformation, MagentoRest.V1ShippingInformation);
    }

    [Fact]
    public void TheBasketPathIsAssembledFromTwoAttestedFragments()
    {
        // R1251: the image carries "/rest/V1" and "carts/mine" as separate standalone strings and no single literal
        // for the joined path. So the replica's hard-coded basket URL is a composition, not an invention, and this
        // pins the composition rather than the string.
        Assert.Equal("carts/mine", MagentoRest.CartsMineToken);
        Assert.Equal("/rest/V1/carts/mine", MagentoRest.Under(MagentoRest.RestBase(null), MagentoRest.CartsMine));
        Assert.Equal("/rest/en_ph/V1/carts/mine", MagentoRest.Under(MagentoRest.RestBase("en_ph"), MagentoRest.CartsMine));
    }

    [Fact]
    public void TheLocaleSegmentSitsBetweenRestAndV1()
    {
        // the image carries both /rest/V1/ppcp/ and rest/en_ph/V1/carts/mine/payment-information
        Assert.Equal("/rest/V1", MagentoRest.RestBase(null));
        Assert.Equal("/rest/V1", MagentoRest.RestBase(string.Empty));
        Assert.Equal("/rest/en_ph/V1", MagentoRest.RestBase("en_ph"));
        Assert.Equal("/rest/en_ph/V1/carts/mine/payment-information",
            MagentoRest.Under(MagentoRest.RestBase("en_ph"), MagentoRest.PaymentInformation));
    }

    [Fact]
    public void TheAdyenPluginPathsAreCarriedBecauseTheImageHasThem()
    {
        Assert.Equal("/adyen/carts/mine/payments-details", MagentoRest.AdyenPaymentsDetails);
        Assert.Equal("/adyen/orders/carts/mine/payment-status", MagentoRest.AdyenPaymentStatus);
    }

    [Fact]
    public void TheEndClothingShapePutsThePrefixInTheHost()
    {
        Assert.Equal("https://api2.endclothing.com/rest/V1", MagentoRest.EndClothingRestHost);
        Assert.Equal("/end/carts/mine/", MagentoRest.EndClothingCartsMine);
    }
}
