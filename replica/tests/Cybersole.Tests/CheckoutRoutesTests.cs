using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1255: the checkout route family the image carries, and the two shapes the replica had assumed.
///
/// <para>
/// The distinguishing fact is the fragment versus the query. The replica's Magento page step asks for
/// <c>/checkout/#payment</c>, and a fragment never reaches the server, while the image keys the same idea as
/// <c>/checkout/?stage=payment</c> — a query the storefront can act on. Likewise the terminal page is
/// <c>/checkout/success</c> or <c>/checkout/onepage/success/</c> in the image, not <c>/checkout/complete</c>.
/// Both replica spellings are recorded as inferred at their call sites rather than rewritten, because which store
/// uses which page family is not observable.
/// </para>
/// </summary>
public sealed class CheckoutRoutesTests
{
    [Fact]
    public void TheStageFamilyIsKeyedByQueryNotByFragment()
    {
        Assert.Equal("/checkout/?stage=payment", CheckoutRoutes.StagePayment);
        Assert.Equal("/checkout/?stage=placeOrder", CheckoutRoutes.StagePlaceOrder);
        Assert.Equal("/checkout/?stage=shipping", CheckoutRoutes.StageShipping);
        Assert.Equal("/checkout/?step=payment", CheckoutRoutes.StepPayment);
        Assert.DoesNotContain("#", CheckoutRoutes.StagePayment);
    }

    [Fact]
    public void TheTerminalPagesHaveThreeSpellingsAndNoneIsComplete()
    {
        Assert.Equal("/checkout/success", CheckoutRoutes.Success);
        Assert.Equal("/checkout/onepage/success/", CheckoutRoutes.OnePageSuccess);
        Assert.Equal("/checkout/confirmation", CheckoutRoutes.Confirmation);
        Assert.Equal("/checkout/return", CheckoutRoutes.Return);
    }

    [Fact]
    public void TheCartActionsAreCarried()
    {
        Assert.Equal("/checkout/cart/", CheckoutRoutes.Cart);
        Assert.EndsWith("couponCode=", CheckoutRoutes.CartAddCoupon);
        Assert.Equal("/checkout/cart/couponPost/", CheckoutRoutes.CartCouponPost);
        Assert.Equal("/checkout/sidebar/removeItem/", CheckoutRoutes.CartRemoveItem);
    }

    [Fact]
    public void TheControllerPairIsCarriedToo()
    {
        Assert.Equal("/checkout/services/placeorder/", CheckoutRoutes.ServicesPlaceOrder);
        Assert.Equal("/checkout/shippingservices/submitshipping/", CheckoutRoutes.ShippingServicesSubmitShipping);
    }
}
