using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1269: the vendor payment endpoints the image carries, pinned as protocol facts.
///
/// <para>
/// The former <c>PaymentHostGapTests</c> also asserted a three-host table and an <c>IsPaymentHost</c> predicate; those
/// were coverage-report logic living in the product assembly, so they went with the rename. What remains are the
/// strings a payment step would actually send.
/// </para>
/// </summary>
public sealed class VendorPaymentEndpointTests
{
    [Fact]
    public void TheBraintreeMerchantIdIsCarried()
    {
        Assert.Equal("rfbkw27jcwmw2xgp", VendorPaymentEndpoints.Braintree.MerchantId);
        Assert.Equal(2, VendorPaymentEndpoints.Braintree.Paths.Count);
        Assert.All(VendorPaymentEndpoints.Braintree.Paths, p =>
        {
            Assert.Contains("rfbkw27jcwmw2xgp", p);
            Assert.StartsWith("/merchants/", p);
        });
    }

    [Fact]
    public void BraintreeHasTwoHosts()
    {
        Assert.Equal("https://api.braintreegateway.com", VendorPaymentEndpoints.Braintree.ApiHost);
        Assert.Equal("https://assets.braintreegateway.com", VendorPaymentEndpoints.Braintree.AssetHost);
        Assert.Equal(
            "https://api.braintreegateway.com/merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account",
            VendorPaymentEndpoints.Braintree.UrlFor(VendorPaymentEndpoints.Braintree.Paths[0]));
    }

    [Fact]
    public void VippsCarriesItsEnrollmentPair()
    {
        Assert.Equal(3, VendorPaymentEndpoints.Vipps.Paths.Count);
        Assert.Equal("https://api.vipps.no", VendorPaymentEndpoints.Vipps.ApiHost);
        Assert.Equal("checkout.vipps.no", VendorPaymentEndpoints.Vipps.CheckoutHost);

        var urls = VendorPaymentEndpoints.Vipps.Urls();
        Assert.Equal(2, urls.Count);
        Assert.EndsWith("/adyen-card-enrollment/initiate", urls[0]);
        Assert.EndsWith("/adyen-card-enrollment/commit", urls[1]);
    }

    [Fact]
    public void TheVippsWordingIsRecordedNotInterpreted()
    {
        Assert.Contains("VippsNo", VendorPaymentEndpoints.Vipps.Messages);
        Assert.Contains("3DS Unsupported (VippsNo)", VendorPaymentEndpoints.Vipps.Messages);
    }

    [Fact]
    public void BigCommerceHasOneOrderPaymentPath()
    {
        Assert.Equal("/api/public/v1/orders/payments", VendorPaymentEndpoints.BigCommerce.PaymentsPath);
        Assert.Equal("https://payments.bigcommerce.com/api/public/v1/orders/payments",
            VendorPaymentEndpoints.BigCommerce.Url());
    }
}
