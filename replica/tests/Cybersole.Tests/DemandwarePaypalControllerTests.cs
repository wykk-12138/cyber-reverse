using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1162: the three PayPal controller actions the image carries on an SFCC storefront.
///
/// <c>/Paypal-GetPurchaseUnit</c> (0x146ab044c), <c>/Paypal-GetPaypalOrderId?csrf_token=</c>
/// (0x146ab03ec) and <c>/Paypal-GetOrderDetails?orderId=</c> (0x146ab0394) are storefront controllers,
/// so they compose with the same Sites-{site}-Site path as Product-Show rather than being gateway calls.
/// Only the first has an observed verb — <c>sub_140a50cd0</c> appends it at line 172 and the request at
/// line 179 goes through the GET slot — so only that one is sent; the other two are pinned as strings
/// with their verbs marked Unknown rather than guessed.
/// </summary>
public sealed class DemandwarePaypalControllerTests
{
    [Fact]
    public void TheThreeControllerPathsAreTheImagesOwn()
    {
        Assert.Equal("Paypal-GetPurchaseUnit", DemandwareFlow.PaypalGetPurchaseUnit);
        Assert.Equal("Paypal-GetPaypalOrderId", DemandwareFlow.PaypalGetPaypalOrderId);
        Assert.Equal("Paypal-GetOrderDetails", DemandwareFlow.PaypalGetOrderDetails);
    }

    /// <summary>The query prefixes carry their leading '?', which is how the image stores them.</summary>
    [Fact]
    public void TheQueryPrefixesCarryTheirQuestionMark()
    {
        Assert.Equal("?csrf_token=", DemandwareFlow.PaypalGetPaypalOrderIdQuery);
        Assert.Equal("?orderId=", DemandwareFlow.PaypalGetOrderDetailsQuery);
    }

    /// <summary>They are controller names, so none of them starts or ends with a slash.</summary>
    [Fact]
    public void TheyAreControllerNamesNotAbsolutePaths()
    {
        foreach (var name in new[]
                 {
                     DemandwareFlow.PaypalGetPurchaseUnit,
                     DemandwareFlow.PaypalGetPaypalOrderId,
                     DemandwareFlow.PaypalGetOrderDetails,
                 })
        {
            Assert.DoesNotContain('/', name);
        }
    }
}
