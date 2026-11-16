using System.Linq;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The three hosts the coverage table could not match, and what they turn out to be.
///
/// <para>
/// R948. Criterion (f) wants the original's hosts checkable item by item. The vendor side is clean, but the store side
/// reported three hosts with no registration behind them. All three are payment hosts rather than shops, which is why no
/// store flow claimed them, and each carries concrete paths -- including a Braintree merchant id written into the image.
/// </para>
/// </summary>
public class PaymentHostGapTests
{
    /// <summary>Three hosts, and each is recognised as a payment host rather than a shop.</summary>
    [Fact]
    public void ThreePaymentHostsAreRecorded()
    {
        var hosts = (string[])typeof(PaymentHostGaps)
            .GetField("Hosts", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(3, hosts.Length);
        Assert.All(hosts, h => Assert.True(PaymentHostGaps.IsPaymentHost(h)));
        Assert.False(PaymentHostGaps.IsPaymentHost("api.nike.com"));
        Assert.False(PaymentHostGaps.IsPaymentHost(null));
    }

    /// <summary>
    /// Braintree's merchant id is per-shop rather than per-vendor, so it is recorded as a constant of its own and the two
    /// paths use it. Getting it wrong would send a payment to another merchant.
    /// </summary>
    [Fact]
    public void TheBraintreeMerchantIdIsCarried()
    {
        Assert.Equal("rfbkw27jcwmw2xgp", PaymentHostGaps.Braintree.MerchantId);

        Assert.Equal(2, PaymentHostGaps.Braintree.Paths.Count);
        Assert.All(PaymentHostGaps.Braintree.Paths, p =>
        {
            Assert.Contains("rfbkw27jcwmw2xgp", p);
            Assert.StartsWith("/merchants/", p);
        });
    }

    /// <summary>Both Braintree hosts, since the image names an asset host and an API host separately.</summary>
    [Fact]
    public void BraintreeHasTwoHosts()
    {
        Assert.Equal("https://api.braintreegateway.com", PaymentHostGaps.Braintree.ApiHost);
        Assert.Equal("https://assets.braintreegateway.com", PaymentHostGaps.Braintree.AssetHost);

        Assert.Equal("https://api.braintreegateway.com/merchants/rfbkw27jcwmw2xgp/client_api/v1/payment_methods/paypal_account",
                     PaymentHostGaps.Braintree.UrlFor(PaymentHostGaps.Braintree.Paths[0]));
    }

    /// <summary>Vipps: three paths, two hosts, and the enrollment pair in the image's order.</summary>
    [Fact]
    public void VippsCarriesItsEnrollmentPair()
    {
        Assert.Equal(3, PaymentHostGaps.Vipps.Paths.Count);
        Assert.Equal("https://api.vipps.no", PaymentHostGaps.Vipps.ApiHost);
        Assert.Equal("checkout.vipps.no", PaymentHostGaps.Vipps.CheckoutHost);

        var urls = PaymentHostGaps.Vipps.Urls();
        Assert.Equal(2, urls.Count);
        Assert.EndsWith("/adyen-card-enrollment/initiate", urls[0]);
        Assert.EndsWith("/adyen-card-enrollment/commit", urls[1]);
    }

    /// <summary>
    /// "VippsNo" is recorded as wording and not read as Norway: the "No" could be the country and could be the word. The
    /// same string also appears inside a status message, which is why it is not treated as a locale identifier.
    /// </summary>
    [Fact]
    public void VippsNoIsWordingNotALocale()
    {
        var messages = PaymentHostGaps.Vipps.Messages;

        Assert.Contains("VippsNo", messages);
        Assert.Contains("3DS Unsupported (VippsNo)", messages);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Payments", "PaymentHostGaps.cs"));
        Assert.Contains("could be Norway and could be the word no", doc);
    }

    /// <summary>BigCommerce is a single endpoint and its URL is assembled from the two parts.</summary>
    [Fact]
    public void BigCommerceIsOneEndpoint()
    {
        Assert.Equal("/api/public/v1/orders/payments", PaymentHostGaps.BigCommerce.PaymentsPath);
        Assert.Equal("https://payments.bigcommerce.com/api/public/v1/orders/payments",
                     PaymentHostGaps.BigCommerce.Url());
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}