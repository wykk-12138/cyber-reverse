using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1374: AO's three checkout urls, the origin their senders set, and the two step labels. The bodies are not
/// observed in those functions, so nothing here pretends to know their field names.
/// </summary>
public sealed class AoCheckoutTests
{
    [Fact]
    public void TheThreeUrlsAndOriginAreTheObservedOnes()
    {
        Assert.Equal("https://checkout.ao.com/v2/app/contact", AoCheckout.ContactUrl);
        Assert.Equal("https://checkout.ao.com/v2/app/delivery", AoCheckout.DeliveryUrl);
        Assert.Equal("https://checkout.ao.com/v2/app/payment", AoCheckout.PaymentUrl);
        Assert.Equal("https://checkout.ao.com", AoCheckout.Origin);
        Assert.Equal("Submitting info", AoCheckout.SubmittingInfoMessage);
        Assert.Equal("Getting checkout", AoCheckout.GettingCheckoutMessage);
        Assert.Equal("application/x-www-form-urlencoded", AoCheckout.FormContentType);
        Assert.Equal(new[] { "contact", "delivery", "payment" }, AoCheckout.Steps);
    }

    [Fact]
    public void EachStepHasItsOwnUrl()
    {
        Assert.Equal(AoCheckout.ContactUrl, AoCheckout.UrlFor("contact"));
        Assert.Equal(AoCheckout.DeliveryUrl, AoCheckout.UrlFor("delivery"));
        Assert.Equal(AoCheckout.PaymentUrl, AoCheckout.UrlFor("payment"));
        Assert.Null(AoCheckout.UrlFor("shipping"));
    }
}
