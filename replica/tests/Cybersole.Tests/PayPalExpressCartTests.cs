using System;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>R1378: the PayPal Express cart submission that carries an AddressInput.</summary>
public sealed class PayPalExpressCartTests
{
    [Fact]
    public void ThePathAndVocabularyAreTheObservedOnes()
    {
        Assert.Equal("/cart/paypal", PayPalExpressCart.Path);
        Assert.Equal("EXPRESS", PayPalExpressCart.CheckoutTypeExpress);
        Assert.Equal("OTHER", PayPalExpressCart.CheckoutTypeOther);
        Assert.Equal("Submit info", PayPalExpressCart.SubmitInfoMessage);
        Assert.Equal(new[] { "billingAddress", "checkoutType", "payerId", "nonce", "details" },
            PayPalExpressCart.BodyFieldNames);
        Assert.Equal("https://shop.test/cart/paypal", PayPalExpressCart.UrlFor("https://shop.test/"));
    }

    [Fact]
    public void TheBodyCarriesTheAddressObject()
    {
        var address = new AddressInput { RecipientName = "A", Line1 = "1 Main", City = "Town", CountryCode = "BE" };
        var body = PayPalExpressCart.Body(address, PayPalExpressCart.CheckoutTypeExpress, "P-1", "n-1");

        Assert.Equal("EXPRESS", body["checkoutType"]!.ToObject<string>());
        Assert.Equal("1 Main", body["billingAddress"]!["line1"]!.ToObject<string>());
        Assert.Equal("BE", body["billingAddress"]!["countryCode"]!.ToObject<string>());
        Assert.Equal("P-1", body["payerId"]!.ToObject<string>());
    }

    [Fact]
    public void OnlyTheTwoCheckoutTypesAreAccepted()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            PayPalExpressCart.Body(new AddressInput(), "GUEST", null, null));
    }
}
