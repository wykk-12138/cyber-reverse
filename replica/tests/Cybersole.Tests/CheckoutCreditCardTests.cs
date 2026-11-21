using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1368: CreditCard finalises an order at a relative path, so the order id travels as a path segment and the card
/// fields are the caller's. No card is a fixture here.
/// </summary>
public sealed class CheckoutCreditCardTests
{
    [Fact]
    public void ThePathAndCardFieldsAreTheObservedOnes()
    {
        Assert.Equal("CreditCard", CheckoutCreditCard.OperationName);
        Assert.Equal("api/checkout/v1/orders/", CheckoutCreditCard.OrderPathPrefix);
        Assert.Equal("/finalize", CheckoutCreditCard.FinalizeSuffix);
        Assert.Equal("Submit order", CheckoutCreditCard.SubmitOrderMessage);
        Assert.Equal(new[] { "cardNumber", "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName" },
            CheckoutCreditCard.CardFields);
        Assert.Equal(2867, CheckoutCreditCard.Document.Length);
    }

    [Fact]
    public void TheUrlPutsTheOrderIdInThePath()
    {
        Assert.Equal("https://shop.test/api/checkout/v1/orders/o-1/finalize",
            CheckoutCreditCard.UrlFor("https://shop.test/", "o-1"));
    }

    [Fact]
    public void TheEnvelopeCarriesOperationAndDocument()
    {
        var body = CheckoutCreditCard.Envelope(new JObject());
        Assert.Equal("CreditCard", body["operationName"]!.ToObject<string>());
        Assert.Equal(CheckoutCreditCard.Document, body["query"]!.ToObject<string>());
    }
}
